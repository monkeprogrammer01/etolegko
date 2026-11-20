import sys
import time
import urllib.error
import urllib.request

REQUESTS = 10
TIMEOUT_SECONDS = 60
USER_AGENT = "speed-check/1.0"


def fetch(url: str) -> tuple[float, int]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            body = response.read()
            elapsed = time.perf_counter() - started
    except urllib.error.HTTPError as exc:
        exc.read()
        raise SystemExit(f"HTTP {exc.code} для {url}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Запрос не удался для {url}: {exc.reason}") from exc

    if status != 200:
        raise SystemExit(f"Ожидался HTTP 200, получен {status} для {url}")
    return elapsed, len(body)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print(f"Запуск: python3 {sys.argv[0]} URL", file=sys.stderr)
        raise SystemExit(0 if len(sys.argv) == 2 else 2)

    url = sys.argv[1]
    if not url.startswith(("http://", "https://")):
        raise SystemExit("Адрес должен начинаться с http:// или https://")

    durations: list[float] = []
    sizes: list[int] = []

    for index in range(1, REQUESTS + 1):
        elapsed, nbytes = fetch(url)
        durations.append(elapsed)
        sizes.append(nbytes)
        print(f"{index:2d}/{REQUESTS}  {elapsed:.3f} с  {nbytes} байт")

    total_seconds = sum(durations)
    total_bytes = sum(sizes)
    average_seconds = total_seconds / REQUESTS
    megabits_per_second = (total_bytes * 8) / total_seconds / 1_000_000

    print()
    print(f"Запросов:            {REQUESTS}")
    print(f"Среднее время:       {average_seconds:.3f} с")
    print(f"Скачано всего:       {total_bytes} байт ({total_bytes / 1_000_000:.3f} МБ)")
    print(f"Скорость скачивания: {megabits_per_second:.2f} Мбит/с")


if __name__ == "__main__":
    main()