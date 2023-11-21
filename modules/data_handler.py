import pandas as pd
from datetime import datetime
import re
from pprint import pprint


class DataHandler:
    def __init__(self, date):
        self.base_df = pd.read_csv(f"data/{date}.csv")
        self.telegram_text = self.process_data(self.base_df)

    def read_data(self, path):
        df = pd.read_csv(path)
        return df

    def process_data(self, df):
        df["requirements"] = df["description"].apply(
            self.extract_requirements_from_description
        )

        df_jr = df[
            (~df["title"].str.upper().str.contains("PLENO"))
            & (~df["title"].str.upper().str.contains("SÊNIOR"))
            & (~df["title"].str.upper().str.contains("SENIOR"))
            & (~df["title"].str.upper().str.contains("SR"))
            & (~df["title"].str.upper().str.contains("PL"))
        ]
        df_jr = df_jr.sort_values(by="state")

        self.df_jr_remote = df_jr[(df_jr["is_remote_work"] == True)]
        self.df_jr_hybrids = df_jr[(df_jr["workplace_type"] == "hybrid")]

        text = self.contruct_text(
            [
                {
                    "title_section": "🌐 Vagas Jr - Remotas 🌐 ",
                    "data": self.df_jr_remote,
                    "type": "remote ",
                },
                {
                    "title_section": "🌍 Vagas Jr - Híbridas 🌍",
                    "data": self.df_jr_hybrids,
                    "type": "hybrid",
                },
            ]
        )
        return text

    def extract_requirements_from_description(self, description):
        padrao = re.compile(
            r"Requisitos e qualificações(.*?)Informações adicionais", re.DOTALL
        )
        try:
            requirements = padrao.search(description).group(1).split(";")
            return requirements
        except:
            return ""

    def contruct_text(self, list_of_dict):
        raw_date = datetime.now()

        text = (
            f"📅 Vagas atualizadas dia: *{raw_date.strftime('%d/%m/%Y')}*\n"
            f"Período: *{'Manhã 🌅' if raw_date.hour < 12 else 'Tarde 🌇'}*\n\n "
        )

        for dict in list_of_dict:
            if len(dict["data"]) == 0:
                continue
            text += f"*{self.filter(dict['title_section'])}*\n"
            for _, row in dict["data"].iterrows():
                job_company_name = self.filter(row["career_page_name"])
                job_title = self.filter(row["title"])
                job_url = str(row["job_url"])

                text += f"🏢 {job_company_name}\n"

                if dict["type"] == "hybrid":
                    text += self.filter(f"📍 Local: {row['city']} - {row['state']}\n")

                text += f"🔗 [{job_title}]({job_url})\n\n"

        text += (
            "\n"
            f"Gostou do projeto? Você pode contribuir com uma ⭐️ no repositório:\n"
            "[GitHub \- Junior Zone](https://github.com/Moscarde/Junior_Zone)"
        )
        return text

    def filter(self, text):
        #'_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!' must be escaped with the preceding character '\'.
        return (
            str(text)
            .replace(".", "\.")
            .replace("(", "\(")
            .replace(")", "\)")
            .replace("|", "\|")
            .replace("-", "\-")
            .replace("+", "\+")
            .replace("[", "\[")
            .replace("]", "\]")
            .replace("{", "\{")
            .replace("}", "\}")
            .replace("!", "\!")
            .replace("#", "\#")
            .replace("~", "\~")
            .replace("`", "\`")
            .replace(">", "\>")
            .replace("*", "\*")
            .replace("_", "\_")
            .replace("=", "\=")
            .replace("'", "'")
            .replace('"', '"')
            .replace("<", "\<")
        )

    def export_to_excel(self):
        dfs = [self.df_jr_remote, self.df_jr_hybrids]
        df_excel = pd.concat(dfs, ignore_index=True)[
            [
                "published_date",
                "title",
                "career_page_name",
                "workplace_type",
                "job_url",
                "city",
                "state",
            ]
        ]
        df_excel.columns = [
            "Data",
            "Vaga",
            "Nome da Empresa",
            "Tipo de Trabalho",
            "URL",
            "Cidade",
            "Estado",
        ]
        date = datetime.now().date()
        df_excel.to_excel(f"data/{date}.xlsx", index=False)

        with pd.ExcelWriter("data/jobs.xlsx", engine="openpyxl", mode="a") as writer:
            df_excel.to_excel(writer, sheet_name=f"{date}", index=False)

        return df_excel


if __name__ == "__main__":
    data = DataHandler("data/2023-11-21")
    pprint(data)
