import asyncio
import logging
import traceback
from dataclasses import dataclass
from pprint import pprint
from typing import Any, AsyncGenerator, Callable, Dict, List

from rich import box
from rich.live import Live
from rich.panel import Panel
from rich.progress import *
from rich.table import Table

from openi.refactor.constants import DESC_PREFIX, DESC_WIDTH, ITALIC, OVERALL_DESC, RESET
from openi.refactor.plugins.errors import RequestConnectionError, UploadError, err2str

logger = logging.getLogger(__name__)


class SpinnerColumn(ProgressColumn):
    """A column with a 'spinner' animation.

    Args:
        spinner_name (str, optional): Name of spinner animation. Defaults to "dots".
        style (StyleType, optional): Style of spinner. Defaults to "progress.spinner".
        speed (float, optional): Speed factor of spinner. Defaults to 1.0.
        finished_text (TextType, optional): Text used when task is finished. Defaults to " ".
    """

    def __init__(
        self,
        spinner_name: str = "dots",
        style: Optional[StyleType] = "progress.spinner",
        speed: float = 1.0,
        finished_text: TextType = "",
        failed_text: TextType = "[red]✗",
        table_column: Optional[Column] = None,
    ):
        self.spinner = Spinner(spinner_name, style=style, speed=speed)
        self.finished_text = Text.from_markup(finished_text) if isinstance(finished_text, str) else finished_text
        self.failed_text = Text.from_markup(failed_text) if isinstance(failed_text, str) else failed_text
        super().__init__(table_column=table_column)

    def set_spinner(
        self,
        spinner_name: str,
        spinner_style: Optional[StyleType] = "progress.spinner",
        speed: float = 1.0,
    ) -> None:
        """Set a new spinner.

        Args:
            spinner_name (str): Spinner name, see python -m rich.spinner.
            spinner_style (Optional[StyleType], optional): Spinner style. Defaults to "progress.spinner".
            speed (float, optional): Speed factor of spinner. Defaults to 1.0.
        """
        self.spinner = Spinner(spinner_name, style=spinner_style, speed=speed)

    def render(self, task: "Task") -> RenderableType:
        text = self.spinner.render(task.get_time())

        if task.stop_time is not None:
            text = self.failed_text

        if task.finished:
            text = self.finished_text

        return text


class BarColumn(ProgressColumn):
    """Renders a visual progress bar.

    Args:
        bar_width (Optional[int], optional): Width of bar or None for full width. Defaults to 40.
        style (StyleType, optional): Style for the bar background. Defaults to "bar.back".
        complete_style (StyleType, optional): Style for the completed bar. Defaults to "bar.complete".
        finished_style (StyleType, optional): Style for a finished bar. Defaults to "bar.finished".
        pulse_style (StyleType, optional): Style for pulsing bars. Defaults to "bar.pulse".
    """

    def __init__(
        self,
        bar_width: Optional[int] = 40,
        style: StyleType = "bar.back",
        finished_style: StyleType = "green4",
        complete_style: StyleType = "gold3",
        pulse_style: StyleType = "grey58",
        table_column: Optional[Column] = None,
    ) -> None:
        self.bar_width = bar_width
        self.style = style
        self.complete_style = complete_style
        self.finished_style = finished_style
        self.pulse_style = pulse_style
        super().__init__(table_column=table_column)

    def render(self, task: "Task") -> ProgressBar:
        """Gets a progress bar widget for a task."""
        return ProgressBar(
            total=max(0, task.total) if task.total is not None else None,
            completed=max(0, task.completed),
            width=None if self.bar_width is None else max(1, self.bar_width),
            pulse=not task.started,
            animation_time=task.get_time(),
            style=self.style,
            complete_style=self.complete_style,
            finished_style=self.finished_style,
            pulse_style=self.pulse_style,
        )


class TransferSpeedColumn(ProgressColumn):
    """Renders human readable transfer speed."""

    def render(self, task: "Task") -> Text:
        """Show data transfer speed."""
        speed = task.finished_speed or task.speed
        if speed is None:
            # sp = filesize.decimal(int(task.total))
            # return Text(f"{sp}/s", style="grey58")
            return Text(f"?", style="green4")
        data_speed = readable_bytes(int(speed))  # filesize.decimal(int(speed))
        return Text(f"{data_speed}/s", style="green4")


class SummaryTransferSpeedColumn(ProgressColumn):
    """Renders human readable transfer speed."""

    def render(self, task: "Task") -> Text:
        """Show data transfer speed."""

        completed = task.fields.get("completed_bytes", None)
        time_elapsed = task.elapsed or 0
        speed = completed / time_elapsed if time_elapsed > 0 and completed is not None else None
        if speed is None:
            # sp = filesize.decimal(int(task.total))
            # return Text(f"{sp}/s", style="grey58")
            return Text(f"?", style="green4")
        data_speed = readable_bytes(int(speed))  # filesize.decimal(int(speed))
        return Text(f"{data_speed}/s", style="green4")


class SummaryTotalFileSizeColumn(ProgressColumn):
    """Renders total filesize."""

    def render(self, task: "Task") -> Text:
        """Show data completed."""
        # data_size = filesize.decimal(int(task.total)) if task.total is not None else ""
        total = task.fields["fields"]["total_bytes"] or None
        data_size = readable_bytes(int(total)) if total is not None else ""
        return Text(data_size, style="grey58")


class TotalFileSizeColumn(ProgressColumn):
    """Renders total filesize."""

    def render(self, task: "Task") -> Text:
        """Show data completed."""
        # data_size = filesize.decimal(int(task.total)) if task.total is not None else ""
        data_size = readable_bytes(int(task.total)) if task.total is not None else ""
        return Text(data_size, style="grey58")


class MofNCompleteColumn(ProgressColumn):
    """Renders completed count/total, e.g. '  10/1000'.

    Best for bounded tasks with int quantities.

    Space pads the completed count so that progress length does not change as task progresses
    past powers of 10.

    Args:
        separator (str, optional): Text to separate completed and total values. Defaults to "/".
    """

    def __init__(self, separator: str = "/", table_column: Optional[Column] = None):
        self.separator = separator
        super().__init__(table_column=table_column)

    def render(self, task: "Task") -> Text:
        """Show completed/total."""
        completed = int(task.completed)
        total = int(task.total) if task.total is not None else "?"
        total_width = len(str(total))
        return Text(f"{completed:{total_width}d}{self.separator}{total}", style="grey58")


class TimeElapsedColumn(ProgressColumn):
    """Renders time elapsed."""

    def __init__(self, style: str = "grey58", table_column: Optional[Column] = None) -> None:
        self.style = style
        super().__init__(table_column=table_column)

    def render(self, task: "Task") -> Text:
        """Show time elapsed."""
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("-:--:--", style=self.style)
        delta = timedelta(seconds=max(0, int(elapsed)))
        return Text(str(delta), style=self.style)


class DownloadColumn(ProgressColumn):
    """Renders file size downloaded and total, e.g. '0.5/2.3 GB'.

    Args:
        binary_units (bool, optional): Use binary units, KiB, MiB etc. Defaults to False.
    """

    def __init__(self, binary_units: bool = False, table_column: Optional[Column] = None) -> None:
        self.binary_units = binary_units
        super().__init__(table_column=table_column)

    def render(self, task: "Task") -> Text:
        """Calculate common unit for completed and total."""
        completed = int(task.completed)

        unit_and_suffix_calculation_base = int(task.total) if task.total is not None else completed
        if self.binary_units:
            unit, suffix = filesize.pick_unit_and_suffix(
                unit_and_suffix_calculation_base,
                ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"],
                1024,
            )
        else:
            unit, suffix = filesize.pick_unit_and_suffix(
                unit_and_suffix_calculation_base,
                ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
                1000,
            )
        precision = 0 if unit == 1 else 1

        completed_ratio = completed / unit
        completed_str = f"{completed_ratio:,.{precision}f}"

        if task.total is not None:
            total = int(task.total)
            total_ratio = total / unit
            total_str = f"{total_ratio:,.{precision}f}"
        else:
            total_str = "?"

        download_status = f"{completed_str}/{total_str} {suffix}"
        download_text = Text(download_status, style="green4")  # "progress.download")
        return download_text


def trim_desc(desc: str, width: int = DESC_WIDTH, preffix: str = DESC_PREFIX) -> str:
    if len(desc) > width:
        index_len = width - len(preffix)
        desc = preffix + desc[-index_len:]
    return desc


def readable_bytes(byte: int) -> str:
    units = ["bytes", "KiB", "MiB", "GiB", "TiB"]
    index = 0

    if byte < 1024:
        return f"{byte}{units[index]}"

    while byte >= 1024 and index < len(units) - 1:
        byte /= 1024.0
        index += 1
    return f"{byte:.1f}{units[index]}"


@dataclass
class ProgressBarTask:
    desc: str
    total: int
    initial: int
    iter_func: Callable[[Any], AsyncGenerator[int, Any]]
    iter_args: Dict[str, Any] = field(default_factory=Dict)
    error: Union[str, None] = None


@dataclass
class ProgressBarTaskSummary:
    task_id: str
    desc: str
    total: int
    completed: int
    success: bool
    error: Optional[str] = None


class ProgressBarSession:
    """Manager for multiple rich progress bars. One instance can hold multiple bars."""

    # dark_goldenrod, steel_blue, grey58,gold3,green4
    def __init__(self, refresh_per_second: int = 4):
        self.overall_progress = None
        self.overall_task_id = None
        self.total_tasks = 0

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            # DownloadColumn(binary_units=True),
            TextColumn("{task.percentage:>3.0f}%"),
            TransferSpeedColumn(),
            TotalFileSizeColumn(),
            TimeElapsedColumn(),
        )
        self.tasks_summary: list[ProgressBarTask] = []
        self.refresh_per_second = refresh_per_second
        self._live = None

    def enable_overall_progress(self, total_tasks: int, total_bytes: int, overall_desc: str, max_workers: int):
        """启用总体进度条"""
        self.total_tasks = total_tasks
        self.overall_progress = Progress(
            SpinnerColumn(),
            TextColumn("[grey58]{task.description}"),
            MofNCompleteColumn(),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            SummaryTransferSpeedColumn(),
            SummaryTotalFileSizeColumn(),
            TimeElapsedColumn(),
        )
        self.overall_task_id = self.overall_progress.add_task(
            OVERALL_DESC.format(max_workers=max_workers, desc=overall_desc),
            total=total_tasks,
            fields=dict(total_bytes=total_bytes, completed_bytes=0),
        )

    def __enter__(self):
        table = Table.grid()
        if self.overall_progress is not None:
            overall = Panel.fit(
                self.overall_progress,
                box=box.SQUARE,
                # title=OVERALL_TITLE,
                border_style="dark_goldenrod",
                title_align="right",
            )
            table.add_row(overall)
        table.add_row(self.progress)
        self._live = Live(table, refresh_per_second=self.refresh_per_second)
        self._live.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)

    def get_task(self, task_id: int) -> Task:
        return self.progress.tasks[task_id]

    def add_task(self, desc: str, total: int, initial: int = 0):
        task_id = self.progress.add_task(trim_desc(desc), total=total, completed=initial, start=False, full_desc=desc)
        return task_id

    def start_task(self, task_id: int):
        self.progress.start_task(task_id)

    def update_task(self, task_id: int, advance: int):
        self.progress.update(task_id, advance=advance)

    def update_task_err(self, task_id: int, err: str):
        self.progress.update(task_id, error=err)

    def stop_task(self, task_id: int):
        self.progress.stop_task(task_id)

    def update_overall_task(self, advance: int, advance_bytes: int = 0):
        if self.overall_progress is not None and self.overall_task_id is not None:
            completed_bytes = self.overall_progress.tasks[self.overall_task_id].fields.get("completed_bytes", 0)
            new_bytes = completed_bytes + advance_bytes
            updated_fields = dict(completed_bytes=new_bytes)
            self.overall_progress.update(
                self.overall_task_id,
                advance=advance,
            )
            self.overall_progress.tasks[self.overall_task_id].fields.update(updated_fields)

    def get_tasks_summary(self) -> List[ProgressBarTask]:
        return self.tasks_summary

    async def run_task(self, task: ProgressBarTask) -> None:
        """运行单个任务"""
        task_id = self.add_task(desc=task.desc, total=task.total, initial=task.initial)
        try:
            completed = 0 + task.initial
            start_flag: bool = False

            async for chunk in task.iter_func(**task.iter_args):
                if not start_flag:
                    _ = chunk
                    self.start_task(task_id)
                    start_flag = True

                self.update_task(task_id, advance=chunk)
                completed += chunk

        except Exception as e:
            logger.error(f"run_task Failed: {e}")
            if isinstance(e, RequestConnectionError):
                task.error = err2str(e)
                # traceback.print_exc()
            else:
                raise e

        finally:
            self.stop_task(task_id)
            self.tasks_summary.append(task)
            self.update_overall_task(1, completed)

    async def run_task_without_bar(self, task: ProgressBarTask) -> None:
        try:
            completed = 0 + task.initial
            async for chunk in task.iter_func(**task.iter_args):
                completed += chunk  # 仅执行迭代，不更新进度条

        except Exception as e:
            logger.error(f"run_task_without_bar Failed: {e}")
            if isinstance(e, RequestConnectionError):
                task.error = err2str(e)
                # traceback.print_exc()
            else:
                raise e

        finally:
            self.tasks_summary.append(task)
            self.update_overall_task(1, completed)

    async def run_tasks_with_semaphore(
        self,
        tasks: List[ProgressBarTask],
        max_workers: int,
        overall_only: bool = False,
    ) -> List[ProgressBarTask]:
        """使用信号量控制并发执行任务"""
        semaphore = asyncio.Semaphore(max_workers)

        async def run_task_with_semaphore(task: ProgressBarTask):
            async with semaphore:
                if overall_only:
                    await self.run_task_without_bar(task)
                else:
                    await self.run_task(task)

        try:
            await asyncio.gather(*(run_task_with_semaphore(t) for t in tasks))
        except Exception as e:
            raise e

        return self.get_tasks_summary()


async def progress_bar_task(task: ProgressBarTask, session: ProgressBarSession) -> Union[ProgressBarTask, None]:
    """运行单个进度条任务 - 兼容性函数"""
    await session.run_task(task)
    return p.get_tasks_summary()[0] if session.get_tasks_summary() else None


async def run_task_with_semaphore(task: ProgressBarTask, session: ProgressBarSession, semaphore: asyncio.Semaphore):
    """使用信号量运行任务 - 兼容性函数"""
    async with semaphore:
        await session.run_task(task)


async def progress_bar_session(
    tasks: List[ProgressBarTask],
    overall_desc: str,
    max_workers: int,
) -> List[ProgressBarTask]:
    """原有的进度条会话函数 - 兼容性保持"""
    session = ProgressBarSession()
    total = len(tasks)
    if total > 1:
        session.enable_overall_progress(total_tasks=total, overall_desc=overall_desc, max_workers=max_workers)

    with session:
        return await session.run_tasks_with_semaphore(tasks, max_workers)


async def dummy_iter_func(total: Any) -> AsyncGenerator[int, None]:
    """Dummy iterator function for testing purposes."""
    speed_lower_bond = 1024 * 1024 * 5  # 5 MB
    complete = 0
    while complete < total:
        remaining = total - complete

        if remaining <= speed_lower_bond:
            i = remaining
        else:
            # 随机生成 speed_lower_bond 到 total 之间的值（但不超过剩余大小）
            max_chunk = min(remaining, total // 10)  # 最大块大小为总大小的10%
            if max_chunk <= speed_lower_bond:
                i = remaining
            else:
                i = random.randint(speed_lower_bond, max_chunk)

        complete += i
        yield i
        await asyncio.sleep(1)  # Simulate some delay


if __name__ == "__main__":
    from time import sleep

    p = ProgressBarSession()
    task = ProgressBarTask(
        desc="Test Task",
        total=982138212,
        initial=0,
        iter_func=dummy_iter_func,  # Dummy iterator
        iter_args=dict(total=982138212),  # Argument for dummy iterator
    )

    with p:
        task_s = asyncio.run(progress_bar_task(task, p))

    for k, v in task_s.__dict__.items():
        print(f"{k}: {v}")
