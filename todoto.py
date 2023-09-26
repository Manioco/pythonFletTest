import flet as ft
import sqlite3
import time
import glob
import os


"""
Fazer uma verificação para garantir que nenhuma tarefa seja repetida
Criar um código para identificar cada tarefa
adicionar as colunas de código nos databases
criar um database de LOG
inserir um banco de dados para os ativos
inserir um banco de dados para os deletados
"""



# Class to create tasks
class Task(ft.UserControl):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(expand=1)

        self.display_view = ft.Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )

        return ft.Column(controls=[self.display_view, self.edit_view])

    async def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        await self.update_async()

    async def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        await self.update_async()

    async def status_changed(self, e):
        self.completed = self.display_task.value
        await self.task_status_change(self)

    async def delete_clicked(self, e):
        await self.task_delete(self)


# Class to create the app
class TodoApp(ft.UserControl):
    def build(self):
        self.new_task = ft.TextField(
            hint_text="What needs to be done?", on_submit=self.add_clicked, expand=True
        )
        self.tasks = ft.Column()

        self.filter = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text="all"), ft.Tab(text="active"), ft.Tab(text="completed")],
        )

        self.items_left = ft.Text("0 items left")

        # application's root control (i.e. "view") containing all other controls
        return ft.Column(
            width=600,
            controls=[
                ft.Row(
                    [ft.Text(value="Todos", style="headlineMedium")], alignment="center"
                ),
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(
                            icon=ft.icons.ADD, on_click=self.add_clicked
                        ),
                    ],
                ),
                ft.Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        ft.Row(
                            alignment="spaceBetween",
                            vertical_alignment="center",
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(
                                    text="Clear completed", on_click=self.clear_clicked
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    async def add_clicked(self, e):
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            await self.new_task.focus_async()
            await self.update_async()

    async def task_status_change(self, task):
        await self.update_async()

    async def task_delete(self, task):
        self.tasks.controls.remove(task)
        await self.update_async()

    async def tabs_changed(self, e):
        await self.update_async()

    async def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                await self.task_delete(task)

    async def update_async(self):
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.completed == False)
                or (status == "completed" and task.completed)
            )
            if not task.completed:
                count += 1
        self.items_left.value = f"{count} active item(s) left"
        await super().update_async()


def db_execute(date:str, query, params = []):
    with sqlite3.connect(f'database{date}.db') as con:
        cur = con.cursor()
        cur.execute(query, params)
        con.commit()
        print(f"Executed query: {query}")
        return cur.fetchall()

def delete_old_databases(current_date: str):
    # Obtém uma lista de todos os bancos de dados no diretório atual
    database_files = glob.glob('*.db')

    for db_file in database_files:
        # Extrai a data do nome do arquivo (assumindo que o formato seja "tasksDD-MM-YYYY.db")
        filename = os.path.basename(db_file)
        date_part = filename.replace('tasks', '').replace('.db', '')

        # Compara a data do arquivo com a data atual
        if date_part != current_date:
            # Se a data do arquivo for diferente da data atual, exclua o arquivo
            os.remove(db_file)
            print(f"Deleted old database: {db_file}")

# async function to create the page
async def main(page: ft.Page):
    page.title = "ToDo App"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    await page.update_async()

    # create application instance
    # date = time.strftime("%d%m%Y")
    date = time.strftime("%m")
    delete_old_databases(date)
    db_execute(date, f'CREATE TABLE IF NOT EXISTS tasks{date} (name, status)')
    app = TodoApp(date)

    # add application's root control to the page
    await page.add_async(app)


ft.app(main)