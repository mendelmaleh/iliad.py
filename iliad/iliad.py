import textwrap

import aiohttp
import parsel


class Usage:
    def __init__(self, root: parsel.Selector) -> "Usage":
        self.calls = root.css(".conso__text").re_first('Chiamate: <span class="red">(.*)</span>')
        self.calls_cost = root.css(".conso__text").re_first('Consumi voce: <span class="red">(.*)</span>')

        self.sms = root.css(".conso__text").re_first('<span class="red">(.*) SMS</span>')
        self.sms_cost = root.css(".conso__text").re_first('SMS extra: <span class="red">(.*)</span>')

        self.mms = root.css(".conso__text").re_first('<span class="red">(.*) MMS<br></span>')
        self.mms_cost = root.css(".conso__text").re_first('Consumi MMS: <span class="red">(.*)</span>')

        self.data = root.css(".conso__text").re_first('<span class="red">(.*)</span> / .*<br>')
        self.data_limit = root.css(".conso__text").re_first('<span class="red">.*</span> / (.*)<br>')
        self.data_cost = root.css(".conso__text").re_first('Consumi Dati: <span class="red">(.*)</span>')
        self.data_extra = root.css(".conso__text").re_first(
            r'Consumi Dati: <span class="red">.*</span><br>\s+<span class="red">(.*)</span>'
        )

    def __str__(self):
        return (
            f"calls: {self.calls}, cost: {self.calls_cost}\n"
            f"sms: {self.sms}, cost: {self.sms_cost}\n"
            f"mms: {self.mms}, cost: {self.mms_cost}\n"
            f"data: {self.data} / {self.data_limit},  cost: {self.data_cost}, extra: {self.data_extra}"
        )


class Account:
    async def _get_html(self, user: str, password: str):
        async with aiohttp.ClientSession() as session:
            url = "https://www.iliad.it/account/"
            data = {"login-ident": user, "login-pwd": password}
            async with session.post(url, data=data) as resp:
                self.html = await resp.text()

    def _get_html_mock(self):
        with open("saved", "r") as f:
            self.html = f.read()

    def __str__(self):
        return (
            f"name: {self.name} id: {self.id} number: {self.number}\n"
            f"local:\n{textwrap.indent(str(self.local), '  ')}\nroaming:\n{textwrap.indent(str(self.roaming), '  ')}"
        )


async def get(user: str, password: str) -> Account:
    self = Account()
    await self._get_html(user, password)
    # self._get_html_mock()

    root = parsel.Selector(text=self.html)

    self.local = Usage(root.css(".conso-local"))
    self.roaming = Usage(root.css(".conso-roaming"))

    info = root.css(".current-user__infos")[0]
    self.name = info.css(".bold::text").get()
    self.id = info.css(".smaller").re_first(r"ID utente: (\d+)")
    self.number = info.css(".smaller").re_first("Numero: ([0-9 ]+)")

    return self
