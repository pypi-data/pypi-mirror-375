from typing import Any, Literal

from logis.data_type.unitable import NumberUnit


def split_integer(
    total: int,
    n: int,
    mode: Literal["limit_parts", "limit_per_part"] = "limit_parts",
    order: Literal["asc", "desc"] = "desc",
):
    """
    将整数尽可能平均分成parts份,每份都需要是整数

    Args:
        total: 总整数
        n: 需要分成的份数或每份的值
        mode: 模式
        order: 排序方式
    """
    n = int(n)
    assert n > 0, "份数必须大于0"

    arrs = []
    if mode == "limit_parts":
        # 基础值和余数
        base = total // n  # 每份的基础值
        remainder = total % base  # 需要多分配1的份数
        arrs = [
            (remainder, base + 1),
            (n - remainder, base),
        ]
    elif mode == "limit_per_part":
        # 基础值和余数
        base = n  # 每份的基础值
        remainder = total % base
        arrs = [
            (total // base, base),
        ]
        if remainder:
            arrs.append((1, remainder))
    else:
        raise ValueError("mode must be limit_parts or limit_per_part")

    if order == "asc":
        arrs.reverse()
    for times, value in arrs:
        for _ in range(times):
            yield value


def get_numeric_value(some: Any):
    """
    获取输入对象的数值
    """
    if isinstance(some, NumberUnit):
        return some.value
    return some
