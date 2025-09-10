# hamoni/test/utils/data_utils.py
import pandas as pd
import pytz
from pathlib import Path
from typing import List, Optional, Union, Tuple, Dict, Any
import os
from urllib.request import urlretrieve
import zipfile
import csv
from binance.client import Client
import itertools
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging
import gc
from .config import FUTURES_DATA_DIR, SPOT_DATA_DIR, PROJECT_ROOT

import asyncio
import aiohttp
import tempfile
from io import BytesIO

import re

from tqdm import tqdm

# 상수 정의
MAX_WORKERS = 10
BATCH_SIZE = 10
DEFAULT_INTERVAL = '60m'
COLUMNS = [
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_volume', 'count',
    'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'
]
    
def _norm_interval_for_binance(interval: str) -> str:
    """우리 내부 표기 → Binance 표기(1h, 4h, 1d ...)"""
    mapping = {
        '60m': '1h', '240m': '4h', '360m': '6h',
        '720m': '12h', '1440m': '1d',
        '1m': '1m', '5m': '5m', '15m': '15m',
        '30m': '30m', '1h': '1h', '4h': '4h', '6h': '6h',
        '12h': '12h', '1d': '1d', '1w': '1w'
    }
    return mapping.get(interval, interval)

def get_data(
    symbol: str,
    interval: str = DEFAULT_INTERVAL,
    start: Optional[str] = None,
    end: Optional[str] = None,
    data_type: str = 'futures'
) -> pd.DataFrame:
    """OHLCV 데이터를 로드하고 전처리합니다.
    
    Args:
        symbol: 자산 심볼 (e.g. ``"BTCUSDT"``).
        interval: 시간 간격 (e.g. ``"60m"``).
        start: 시작 날짜 (e.g. ``"2024-01-01"``).
        end: 종료 날짜 (e.g. ``"2025-01-01"``).
        data_type: 데이터 타입 (e.g. ``"futures"`` 또는 ``"spot"``).
    
    Returns:
        pd.DataFrame: 전처리된 OHLCV 데이터
    
    Raises:
        FileNotFoundError: 데이터 파일이 존재하지 않는 경우
        DataProcessingError: 데이터 처리 중 오류 발생
    """
    try:
        data_dir = FUTURES_DATA_DIR if data_type == 'futures' else SPOT_DATA_DIR
        tz = pytz.timezone('Asia/Seoul')
        data_path = Path(data_dir[interval]) / f'{symbol}.csv'
        
        if not data_path.exists():
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")
        
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df.index = df.index.tz_localize(pytz.UTC).tz_convert(tz)
        
        if start is not None:
            df = df[start:]
        if end is not None:
            df = df[:end]
        
        return df
    
    except Exception as e:
        raise DataProcessingError(f"데이터 처리 중 오류 발생: {str(e)}")
    

def generate_data_for_backtest(
    symbols: List[str],
    start_YY_MM: Union[str, datetime],
    end_YY_MM: Union[str, datetime],
    intervals: List[str],
    data_types: List[str]
) -> None:
    """백테스트용 데이터를 생성합니다.
    
    주의: 병렬처리를 사용하므로 Jupyter Notebook에서 실행하지 마세요.

    Args:
        symbols: 심볼 리스트 ['BTCUSDT', 'ETHUSDT', ...]
        start_date: 시작 날짜 (YYYY-MM)
        end_date: 종료 날짜 (YYYY-MM)
        intervals: 시간 간격 리스트 시간 간격 리스트 ['1m', '5m', '15m','60m','240m','360m','720m','1440m','1w']
        data_types: 데이터 타입 리스트 ['futures', 'spot']
    """
    
    setup_logging()
    # start_YY_MM 포멧에 안맞으면 오류 발생
    if not isinstance(start_YY_MM, str) or not isinstance(end_YY_MM, str):
        raise ValueError("start_YY_MM 또는 end_YY_MM는 문자열이어야 합니다.")
    if not re.match(r'^\d{4}-\d{2}$', start_YY_MM) or not re.match(r'^\d{4}-\d{2}$', end_YY_MM):
        raise ValueError("start_YY_MM 또는 end_YY_MM는 YYYY-MM 형식이어야 합니다.")

    # YYYY-MM 파싱
    if isinstance(start_YY_MM, str):
        start_date = datetime.strptime(start_YY_MM, '%Y-%m')
    else:
        start_date = datetime(start_YY_MM.year, start_YY_MM.month, 1)

    if isinstance(end_YY_MM, str):
        end_date = datetime.strptime(end_YY_MM, '%Y-%m')
    else:
        end_date = datetime(end_YY_MM.year, end_YY_MM.month, 1)

    total_tasks = len(data_types) * len(intervals) * len(symbols)

    print(f"📊 백테스트 데이터 생성을 시작합니다.")
    print(f"   - 심볼 수: {len(symbols)}")
    print(f"   - 시간 간격: {intervals}")
    print(f"   - 데이터 타입: {data_types}")
    print(f"   - 총 작업 수: {total_tasks}")
    print(f"   - 기간: {start_date.strftime('%Y-%m')} ~ {end_date.strftime('%Y-%m')}")
    print("=" * 60)

    completed_tasks = 0

    for data_type_idx, data_type in enumerate(data_types):
        print(f"\n🔄 데이터 타입: {data_type} ({data_type_idx + 1}/{len(data_types)})")

        data_type_dir = Path(PROJECT_ROOT) / f'data_{data_type}'
        data_type_dir.mkdir(exist_ok=True)

        for interval_idx, interval in enumerate(intervals):
            print(f"  ⏰ 시간 간격: {interval} ({interval_idx + 1}/{len(intervals)})")

            # 내부 디렉토리 이름은 기존 규칙 유지
            str_interval = (f"{interval}" if 'm' in interval else
                            f'{int(interval.replace("h",""))*60}m' if 'h' in interval
                            else f'{int(interval.replace("d",""))*1440}m')

            base_dir = Path(f"{data_type_dir}/data_{str_interval}")
            base_dir.mkdir(exist_ok=True)

            with tqdm(total=len(symbols),
                      desc=f"    💰 {data_type}-{interval} 처리 중",
                      unit="심볼",
                      leave=False) as pbar:

                for i in range(0, len(symbols), BATCH_SIZE):
                    symbol_batch = symbols[i:i + BATCH_SIZE]

                    with ProcessPoolExecutor(max_workers=BATCH_SIZE) as executor:
                        args = [
                            (symbol, interval, base_dir, start_date, end_date, data_type)
                            for symbol in symbol_batch
                        ]
                        list(executor.map(process_symbol, args))

                    pbar.update(len(symbol_batch))
                    completed_tasks += len(symbol_batch)

            gc.collect()

    print("\n" + "=" * 60)
    print(f"✅ 모든 작업이 완료되었습니다! (총 {completed_tasks}개 작업)")
    print(f"📁 데이터가 저장된 위치: {PROJECT_ROOT}")


def make_unofficial_interval(
    symbols: List[str],
    resample_minutes: int,
    data_type: str
) -> None:
    """비공식 시간 간격의 데이터를 생성합니다.
    
    Args:
        symbols: 심볼 리스트
        resample_minutes: 리샘플링할 분 단위 45분 ->45, 2시간 -> 120
        data_type: 데이터 타입, [data_futures,data_spot]
    """
    def resampler(df: pd.DataFrame, resample_minutes: int = 45) -> pd.DataFrame:
        """데이터프레임을 리샘플링합니다."""
        if not isinstance(df.index, pd.DatetimeIndex):
            df.set_index('datetime', inplace=True)
        
        return df.resample(f'{resample_minutes}min').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
    
    for symbol in symbols:
        input_path = Path(f'{data_type}/data_5m/{symbol}.csv')
        df_5m = pd.read_csv(input_path, index_col=0, parse_dates=True)
        
        new_df = resampler(df_5m, resample_minutes=resample_minutes)
        
        output_dir = Path(f'{data_type}/data_{resample_minutes}m')
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f'{symbol}.csv'
        new_df.to_csv(output_path)
        
# 내부 함수

class DataProcessingError(Exception):
    """데이터 처리 중 발생하는 예외를 처리하기 위한 커스텀 예외 클래스"""
    pass

def setup_logging() -> None:
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_last_timestamp(file_path: Path) -> Optional[datetime]:
    """파일에서 마지막 데이터의 timestamp를 가져옵니다."""
    if not file_path.exists() or file_path.stat().st_size == 0:
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 파일 끝에서부터 역방향으로 읽기
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            
            if file_size == 0:
                return None
            
            # 마지막 1KB 정도만 읽어서 처리 (대부분의 경우 충분)
            read_size = min(1024, file_size)
            f.seek(file_size - read_size)
            
            # 첫 번째 불완전한 줄 건너뛰기 (중간에서 시작했을 수 있으므로)
            if file_size > read_size:
                f.readline()
            
            # 나머지 줄들 읽기
            lines = f.readlines()
            
            # 마지막부터 유효한 데이터 줄 찾기
            for line in reversed(lines):
                line = line.strip()
                
                if not line or line.startswith('datetime,'):
                    continue
                
                try:
                    dt_str = line.split(',')[0]
                    return pd.to_datetime(dt_str)
                except (IndexError, ValueError):
                    continue
            
            return None
            
    except Exception as e:
        logging.error(f"타임스탬프 읽기 실패 {file_path}: {e}")
        return None


def generate_monthly_urls(
    symbol: str,
    start_ym: datetime,   # 반드시 month-start면 더 좋지만, 그냥 YYYY-MM 형태면 OK
    end_ym: datetime,
    interval: str,
    data_type: str = 'futures'
) -> List[str]:
    """
    Binance Vision monthly klines:
    - futures: https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{YYYY}-{MM}.zip
    - spot   : https://data.binance.vision/data/spot/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{YYYY}-{MM}.zip
    """
    base_url = ("https://data.binance.vision/data/spot/monthly/klines"
                if data_type == 'spot'
                else "https://data.binance.vision/data/futures/um/monthly/klines")

    iv = _norm_interval_for_binance(interval)

    # start_ym, end_ym이 day 포함이어도 month 범위로 정규화
    cur = datetime(start_ym.year, start_ym.month, 1)
    end = datetime(end_ym.year, end_ym.month, 1)

    urls: List[str] = []
    while cur <= end:
        urls.append(f"{base_url}/{symbol}/{iv}/{symbol}-{iv}-{cur.year}-{cur.month:02d}.zip")
        # 다음 달
        if cur.month == 12:
            cur = datetime(cur.year + 1, 1, 1)
        else:
            cur = datetime(cur.year, cur.month + 1, 1)
    return urls


# 과거 데이터중 빠진 부분들이 간혹있어 제외
def generate_daily_urls(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    interval: str,
    data_type: str = 'futures'
) -> List[str]:
    """일별 데이터 URL을 생성합니다.
    
    Args:
        symbol: 거래 심볼
        start_date: 시작 날짜
        end_date: 종료 날짜
        interval: 시간 간격
        data_type: 데이터 타입
        
    Returns:
        List[str]: URL 리스트
    """
    base_url = ("https://data.binance.vision/data/spot/daily/klines" 
                if data_type == 'spot' 
                else "https://data.binance.vision/data/futures/um/daily/klines")
    
    urls = []
    if interval == '60m':
        interval = '1h'
    if interval == '240m':
        interval = '4h'
    if interval =='360m':
        interval = '6h'
    if interval =='720m':
        interval = '12h'
    if interval =='1440m':
        interval = '1d'
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        urls.append(f"{base_url}/{symbol}/{interval}/{symbol}-{interval}-{date_str}.zip")
        current_date += timedelta(days=1)
    return urls

def has_header(file_path: Path) -> bool:
    """CSV 파일의 헤더 존재 여부를 확인합니다."""
    try:
        with open(file_path, 'r') as f:
            sniffer = csv.Sniffer()
            sample = ''.join(list(itertools.islice(f, 10)))
            return sniffer.has_header(sample)
    except Exception:
        return False

def download_single_file(args: Tuple[str, Path]) -> bool:
    """단일 파일을 다운로드하고 압축을 해제합니다.
    
    Args:
        args: (url, 추출 디렉토리) 튜플
        
    Returns:
        bool: 성공 여부
    """
    url, extract_dir = args
    try:
        filename = url.split('/')[-1]
        file_path = extract_dir / filename
        
        urlretrieve(url, str(file_path))
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        file_path.unlink()
        return True
    except Exception as e:
        # logging.error(f"파일 처리 오류 {url}: {e}")
        return False

async def _fetch_and_unzip(session, url: str, extract_dir: Path, retries: int = 3, chunk_size: int = 1<<15) -> bool:
    backoff = 0.5
    for attempt in range(retries):
        try:
            async with session.get(url) as resp:
                if resp.status == 404:
                    return False  # 없는 날짜/파일
                resp.raise_for_status()

                # 큰 파일 대비: 디스크 임시파일에 스트리밍 저장 후 unzip
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = Path(tmp.name)
                    async for chunk in resp.content.iter_chunked(chunk_size):
                        tmp.write(chunk)

                try:
                    with zipfile.ZipFile(tmp_path, 'r') as zf:
                        zf.extractall(extract_dir)
                finally:
                    try:
                        tmp_path.unlink(missing_ok=True)
                    except Exception:
                        pass
                return True

        except Exception:
            if attempt == retries - 1:
                return False
            await asyncio.sleep(backoff)
            backoff *= 2


async def _download_and_unzip_async(urls: List[str], extract_dir: Path, concurrency: int = 64, per_host_limit: int = 16, timeout_s: int = 30) -> None:
    if not urls:
        return
    extract_dir.mkdir(parents=True, exist_ok=True)

    timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_s, sock_read=timeout_s)
    connector = aiohttp.TCPConnector(limit=concurrency, limit_per_host=per_host_limit, ttl_dns_cache=300)
    sem = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        async def worker(u):
            async with sem:
                return await _fetch_and_unzip(session, u, extract_dir)

        # 실행 (실패 True/False 무시하고 병합 단계에서 자연스럽게 거름)
        await asyncio.gather(*(worker(u) for u in urls))


def download_and_unzip(urls: List[str], extract_dir: Path, concurrency: Optional[int] = None) -> None:
    """
    기존 시그니처 유지. 내부에서 asyncio 실행.
    concurrency 미지정 시 URL 개수/파일 크기 감안해 동적 설정.
    """
    if not urls:
        return
    # 작은 파일(일봉·4H 등)은 동시성 높게, 큰 파일은 낮게
    c = concurrency or max(16, min(64, len(urls)))
    try:
        asyncio.run(_download_and_unzip_async(urls, extract_dir, concurrency=c))
    except RuntimeError:
        # 이미 이벤트 루프가 돌아가는 환경(Jupyter/서브루프) 보호
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_download_and_unzip_async(urls, extract_dir, concurrency=c))

def process_single_file(file_path: Path) -> Optional[pd.DataFrame]:
    """단일 CSV 파일을 처리합니다."""
    try:
        if has_header(file_path):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_csv(file_path, header=None, names=COLUMNS)
        return df
    except Exception as e:
        logging.error(f"파일 읽기 오류 {file_path}: {e}")
        return None
    finally:
        gc.collect()

def merge_data_files(
    extract_dir: Path,
    output_filename: Path,
    existing_df: Optional[pd.DataFrame] = None  # 호환성만 유지, 내부에서 사용 안 함
) -> None:
    """temp 디렉토리의 일자 CSV들을 메모리 효율적으로 병합(스트리밍 append)."""
    def _date_key(p: Path) -> tuple:
        # 파일명: SYMBOL-INTERVAL-YYYY-MM-DD.csv → 정렬 안정성 확보
        stem = p.stem
        date_str = stem.rsplit('-', 1)[-1]  # YYYY-MM-DD
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
        except Exception:
            d = datetime.min
        return (d.year, d.month, d.day)

    # 기존 파일 마지막 타임스탬프를 빠르게 읽어와서(naive) 중복 방지
    last_ts = get_last_timestamp(output_filename)

    # temp 디렉토리 내 파일들(하루 단위) 날짜 순으로 정렬
    csv_files = sorted(extract_dir.glob('*.csv'), key=_date_key)

    # 결과 파일에 헤더를 쓸지 결정
    header_needed = (not output_filename.exists()) or (output_filename.stat().st_size == 0)

    # 한 번만 열고 계속 append (I/O 오버헤드 감소)
    with open(output_filename, 'a', newline='') as fout:
        for file in csv_files:
            df_raw = process_single_file(file)
            if df_raw is None or df_raw.empty:
                continue

            # 필요한 컬럼만 쓰기 (열 있으면 사용, 없으면 그대로 진행)
            # (process_single_file가 이미 names=COLUMNS로 보장한다면 아래 선택은 없어도 OK)
            try:
                df_raw = df_raw[['open_time', 'open', 'high', 'low', 'close', 'volume']]
            except KeyError:
                pass

            # 최종 포맷으로 즉시 변환 (naive datetime, 정렬)
            # └ tz-aware로 만들지 않음(naive 저장 → +00:00 안 붙음)
            processed = pd.DataFrame({
                'datetime': pd.to_datetime(df_raw['open_time'], unit='ms'),  # naive
                'open':  df_raw['open'],
                'high':  df_raw['high'],
                'low':   df_raw['low'],
                'close': df_raw['close'],
                'volume':df_raw['volume']
            })

            processed.set_index('datetime', inplace=True)
            processed.sort_index(inplace=True)

            # 같은 chunk 내 중복 인덱스 제거 (네트워크/파일 경계 이상치 대비)
            if processed.index.has_duplicates:
                processed = processed[~processed.index.duplicated(keep='last')]

            # 기존 파일의 마지막 시점 이후만 append (파일 간 중복 방지)
            if last_ts is not None:
                processed = processed[processed.index > last_ts]
                if processed.empty:
                    # 이번 파일 내용 전부가 이미 반영됨
                    try:
                        file.unlink()
                    except Exception:
                        pass
                    continue

            # 혹시 tz-aware면 출력 전에 naive로 강제 (안전장치)
            if getattr(processed.index, 'tz', None) is not None:
                processed.index = processed.index.tz_localize(None)

            # 👉 스트리밍 append: 즉시 디스크로
            processed.to_csv(
                fout,
                header=header_needed,
                index_label='datetime',
                date_format="%Y-%m-%d %H:%M:%S"   # +00:00 없는 고정 포맷
            )
            header_needed = False

            # 다음 파일 필터링을 위해 last_ts 갱신
            last_ts = processed.index[-1]

            # 메모리 정리
            del df_raw, processed
            gc.collect()

    # temp 파일 정리
    for file in csv_files:
        try:
            file.unlink()
        except Exception as e:
            logging.error(f"파일 삭제 오류 {file}: {e}")
            
def _date_key(p: Path) -> tuple:
    """
    파일명 끝이 YYYY-MM.csv 또는 YYYY-MM-DD.csv 모두 처리.
    정렬 안정성을 위해 (year, month, day) 튜플을 반환. day가 없으면 1로 둠.
    """
    stem = p.stem  # e.g., SYMBOL-1d-2024-07 or SYMBOL-1d-2024-07-15
    tail = stem.rsplit('-', 1)[-1]  # 'YYYY-MM' or 'YYYY-MM-DD'
    # 일/월 포맷 모두 시도
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            d = datetime.strptime(tail, fmt)
            if fmt == "%Y-%m":
                return (d.year, d.month, 1)
            return (d.year, d.month, d.day)
        except ValueError:
            continue
    # 파싱 실패 시 맨 뒤에서 두 조각을 잡아보는 보호 로직
    parts = tail.split('-')
    try:
        y, m = int(parts[0]), int(parts[1])
        d = int(parts[2]) if len(parts) > 2 else 1
        return (y, m, d)
    except Exception:
        # 최후의 보호: 아주 앞쪽으로 가도록
        return (1, 1, 1)

def process_symbol(args: Tuple[str, str, Path, datetime, datetime, str]) -> bool:
    """
    단일 심볼 처리 (월별 ZIP 사용).
    args: (symbol, interval, base_dir, start_date, end_date, data_type)
    - start_date/end_date: YYYY-MM 기반이어도 datetime이면 OK. month만 쓰임.
    """
    symbol, interval, base_dir, start_date, end_date, data_type = args
    try:
        logging.info(f"처리 중: {symbol} (간격: {interval})")
        output_filename = base_dir / f'{symbol}.csv'
        temp_dir = base_dir / f'temp_dir_{symbol}'

        # 기존 파일이 있으면 마지막 ts 기준 "그 달부터" 다시 받기 (같은 달 일부가 비어있을 수 있으므로)
        last_ts = get_last_timestamp(output_filename)
        if last_ts is not None:
            # 해당 월 1일로 내림
            start_date = datetime(last_ts.year, last_ts.month, 1)
            logging.info(f"{symbol}: {start_date:%Y-%m}부터 재개")
            # 최신 여부 체크는 merge 단계에서 자동 필터링(> last_ts)으로 보장되므로 따로 early return 안 함
        else:
            # 전달받은 start_date를 월초로 정규화
            start_date = datetime(start_date.year, start_date.month, 1)

        # end_date도 월초로 정규화
        end_date = datetime(end_date.year, end_date.month, 1)

        temp_dir.mkdir(parents=True, exist_ok=True)

        # ✅ 월별 ZIP URL 생성
        urls = generate_monthly_urls(symbol, start_date, end_date, interval, data_type)
        if urls:
            # 월 ZIP은 크므로 동시성 너무 높이지 않는 게 유리(디폴트 내부 정책 사용)
            download_and_unzip(urls, temp_dir)
            merge_data_files(temp_dir, output_filename, existing_df=None)
            logging.info(f"{symbol} 처리 완료")

        # temp 정리
        if temp_dir.exists():
            for file in temp_dir.iterdir():
                try:
                    file.unlink()
                except Exception:
                    pass
            try:
                temp_dir.rmdir()
            except Exception:
                pass

        return True
    except Exception as e:
        logging.error(f"심볼 처리 오류 {symbol}: {e}")
        return False
    finally:
        gc.collect()

