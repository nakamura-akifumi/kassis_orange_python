import math

class Paginate:
    def __init__(self, pagetab_count = 5, per_page = 10):
        pass
        self.pagetab_count = pagetab_count
        self.per_page = per_page

    def paginate(self, result_count, current_page):
        paginate_list = []
        pagetab_count = self.pagetab_count
        per_page = self.per_page

        max_page = math.floor((result_count) / per_page)
        if max_page <= pagetab_count:
            sp = current_page
            ep = sp + pagetab_count
        elif current_page > 3 and max_page - 2 > current_page:
            sp = current_page - 2
            ep = sp + pagetab_count
        elif current_page <= 3 and max_page > current_page + pagetab_count:
            sp = 1
            ep = sp + pagetab_count
        else:
            sp = max_page - pagetab_count + 1
            ep = max_page + 1

        for p in range(sp, ep):
            x = {"key": str(p), "display_name": str(p), "current": "0"}
            if p == current_page:
                x.update({"current": "1"})

            paginate_list.append(x)

        paginate = {}
        paginate.update({"list": paginate_list})
        if current_page != 1:
            paginate.update({"first": {"key": "1"}})
        if current_page != max_page:
            paginate.update({"last": {"key": str(max_page)}})
        if current_page - 1 > 1:
            paginate.update({"previous": {"key": str(current_page - 1)}})
        if current_page + 1 <= max_page:
            paginate.update({"next": {"key": str(current_page + 1)}})

        return {"paginate": paginate}

