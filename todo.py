import flet as ft
import sqlite3

class To_do:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.bgcolor = ft.colors.WHITE # Set background color
        self.page.window_width = 350 # Set window width
        self.page.window_height = 650 # Set window height
        self.page.window_resizable = False # Set window to not be resizable
        self.page.window_always_on_top = True # Set window to always be on top
        self.page.scroll = "vertical" # Set scroll to vertical
        self.task = ""
        self.view = "all"
        self.page.title = "Todo APP" # Set window title
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks(name, status)')
        self.results = self.db_execute('SELECT * FROM tasks')
        self.main_page() # Call main page

    def db_execute(self, query, params = []):
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall()

    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label

        if is_checked:
            self.db_execute('UPDATE tasks SET status = 1 WHERE name = ?', params=[label])
        else:
            self.db_execute('UPDATE tasks SET status = 0 WHERE name = ?', params=[label])

        if self.view == "all":
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=[self.view])

        self.update_task_list()

    def tasks_container(self):
        return ft.Container(
            height=self.page.height * 0.8,
            width=self.page.width * 0.9,
            bgcolor=ft.colors.BLUE_50,
            content = ft.Column(
                controls = [
                    ft.Checkbox(label=res[0],
                                on_change=self.checked,
                                value = True if res[1] == 1 else False)
                    for res in self.results if res
                ]
                )
        )
    
    def set_value(self, e):
        self.task = e.control.value
        # print(self.task)

    def update_task_list(self):
        tasks = self.tasks_container()
        self.page.controls.pop()
        self.page.add(tasks)
        self.page.update()
    
    def tabs_changed(self, e):
        if e.control.selected_index == 0:
            self.results = self.db_execute('SELECT * FROM tasks')
            self.view = "all"
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = 0')
            self.view = "doing"
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = 1')
            self.view = "done"
        
        self.update_task_list()


    def add(self, e, input_task):
        name = self.task
        status = 0

        if name:
            self.db_execute(query='INSERT INTO tasks VALUES(?, ?)', params=[name, status])
            input_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_task_list()

    def main_page(self):
        input_task = ft.TextField(
            hint_text='Digite uma tarefa', 
            expand=True,
            on_change=self.set_value
        )
        bt_add = ft.FloatingActionButton(
            icon=ft.icons.ADD,
            on_click=lambda e: self.add(e, input_task)
        )

        input_bar = ft.Row(
            controls={
                input_task,
                bt_add
            }
        )

        tabs = ft.Tabs(
            on_change=self.tabs_changed,
            selected_index=0,
            tabs=[
                ft.Tab(text="Todas"),
                ft.Tab(text="Fazendo"),
                ft.Tab(text="Feito")
            ]
        )

        tasks = self.tasks_container()

        self.page.add(input_bar, tabs, tasks)
        self.update_task_list()


ft.app(To_do)
