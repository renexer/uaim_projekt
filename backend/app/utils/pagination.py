def build_meta(page: int, page_size: int, total: int) -> dict:
    return {"page": page, "pageSize": page_size, "total": total}


def paginate_items(items, page: int, page_size: int):
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], build_meta(page, page_size, total)
