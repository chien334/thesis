# admin_page.py
import flet as ft
import requests

# API configuration
API_BASE_URL = "http://localhost:8000"  # Điều chỉnh URL API server của bạn

class AdminPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/admin")
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

        # Lấy thông tin từ session
        self.username = self.page.session.get("username") or "Admin"
        self.token = self.page.session.get("token")

        # Khởi tạo dữ liệu
        self.users = []
        self.history = []
        self.current_tab = "users"  # Tab mặc định

        # Tạo nút đăng xuất
        self.logout_button = ft.ElevatedButton("Đăng xuất", on_click=self.logout_clicked)

        # AppBar được gán cho thuộc tính appbar của View
        self.appbar = ft.AppBar(
            title=ft.Text("Trang Quản Trị"),
            bgcolor=ft.Colors.BLUE_GREY_100,  # Màu khác cho admin
            actions=[self.logout_button]
        )

        # Tạo các tab dọc bên trái
        self.side_tabs = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(f"Quản trị viên\n{self.username}", 
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_GREY_100,
                    border_radius=ft.BorderRadius(0, 10, 0, 0),  # Top-right corner radius set to 10
                ),
                ft.ElevatedButton(
                    text="Quản lý người dùng",
                    icon=ft.Icons.PEOPLE,
                    on_click=lambda e: self.change_tab("users"),
                    width=200,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=0),
                    ),
                ),
                ft.ElevatedButton(
                    text="Lịch sử phát hiện",
                    icon=ft.Icons.HISTORY,
                    on_click=lambda e: self.change_tab("history"),
                    width=200,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=0),
                    ),
                ),
                ft.Container(expand=True),  # Spacer
                self.logout_button,
            ],
            width=200,
            # bgcolor=ft.Colors.BLUE_GREY_50,
            height=float("inf"),
        )

        # Tạo container cho nội dung tab
        self.tab_content = ft.Container(
            expand=True,
            padding=20,
        )

        # Tạo các thành phần UI cho tab người dùng
        self.users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Tên người dùng")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Vai trò")),
                ft.DataColumn(ft.Text("Hành động"))
            ],
            rows=[]
        )

        # Tạo các thành phần UI cho tab lịch sử
        self.history_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Người dùng")),
                ft.DataColumn(ft.Text("Thời gian")),
                ft.DataColumn(ft.Text("Kết quả")),
                ft.DataColumn(ft.Text("Hành động"))
            ],
            rows=[]
        )

        # Tạo layout chính với Row để chia 2 phần
        self.controls = [
            ft.Row(
                [
                    self.side_tabs,
                    ft.VerticalDivider(width=1),
                    self.tab_content,
                ],
                expand=True,
            )
        ]

        # Tải dữ liệu ban đầu
        self.load_users()
        self.update_tab_content()

    def get_auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def change_tab(self, tab_name: str):
        self.current_tab = tab_name
        if tab_name == "users":
            self.load_users()
        else:
            self.load_history()
        self.update_tab_content()

    def update_tab_content(self):
        if self.current_tab == "users":
            # Hiển thị tab người dùng
            self.tab_content.content = self.create_users_content()
        else:
            # Hiển thị tab lịch sử
            self.tab_content.content = self.create_history_content()
        self.page.update()

    def create_users_content(self):
        # Cập nhật bảng người dùng
        self.users_table.rows = []
        for user in self.users:
            self.users_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(user.get("id", "")))),
                        ft.DataCell(ft.Text(user.get("username", ""))),
                        ft.DataCell(ft.Text(user.get("email", ""))),
                        ft.DataCell(ft.Text("Admin" if user.get("is_admin") else "Người dùng")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Chỉnh sửa",
                                        on_click=lambda e, u=user: self.edit_user(u)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Xóa",
                                        on_click=lambda e, u=user: self.delete_user(u)
                                    )
                                ]
                            )
                        )
                    ]
                )
            )

        # Tạo nút thêm người dùng
        add_user_button = ft.ElevatedButton(
            "Thêm người dùng",
            icon=ft.Icons.ADD,
            on_click=self.add_user
        )

        # Tạo layout cho nội dung
        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("Danh sách người dùng", 
                                  size=24, 
                                  weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            add_user_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=ft.margin.only(bottom=20)
                ),
                ft.Container(
                    content=ft.Column(
                        [self.users_table],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True
                    ),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    padding=10,
                    expand=True
                ),
            ],
            expand=True
        )

    def create_history_content(self):
        # Cập nhật bảng lịch sử
        self.history_table.rows = []
        for item in self.history:
            self.history_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item.get("id", "")))),
                        ft.DataCell(ft.Text(item.get("username", ""))),
                        ft.DataCell(ft.Text(item.get("timestamp", ""))),
                        ft.DataCell(ft.Text(item.get("result", "")[:20] + "...")),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.VISIBILITY,
                                        tooltip="Xem chi tiết",
                                        on_click=lambda e, i=item: self.view_history_detail(i)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Xóa",
                                        on_click=lambda e, i=item: self.delete_history(i)
                                    )
                                ]
                            )
                        )
                    ]
                )
            )

        # Tạo layout cho nội dung
        return ft.Column(
            [
                ft.Container(
                    content=ft.Text("Lịch sử phát hiện", 
                                  size=24, 
                                  weight=ft.FontWeight.BOLD),
                    margin=ft.margin.only(bottom=20)
                ),
                ft.Container(
                    content=ft.Column(
                        [self.history_table],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True
                    ),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    padding=10,
                    expand=True
                ),
            ],
            expand=True
        )

    def load_users(self):
        if not self.token:
            self.users = []
            print("Error: No token available for loading users.")
            # Optionally, redirect to login page
            # self.page.go("/login")
            return
            
        try:
            headers = self.get_auth_header()
            response = requests.get(f"{API_BASE_URL}/users/admin/list", headers=headers)

            if response.status_code == 200:
                self.users = response.json()
                print(f"Loaded {len(self.users)} users.")
            elif response.status_code == 401:
                print("Authentication failed. Redirecting to login.")
                self.page.go("/login")
            else:
                print(f"Error loading users: {response.status_code} - {response.text}")
                self.users = [] # Clear data on error
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching users from API: {e}")
            self.users = [] # Clear data on error

        self.update_tab_content() # Update UI after loading

    def load_history(self):
        if not self.token:
            self.history = []
            print("Error: No token available for loading history.")
             # Optionally, redirect to login page
            # self.page.go("/login")
            return
            
        try:
            headers = self.get_auth_header()
            # Assuming /history/admin returns all history for admin
            response = requests.get(f"{API_BASE_URL}/history/admin", headers=headers)

            if response.status_code == 200:
                self.history = response.json()
                print(f"Loaded {len(self.history)} history items.")
            elif response.status_code == 401:
                print("Authentication failed. Redirecting to login.")
                self.page.go("/login")
            else:
                print(f"Error loading history: {response.status_code} - {response.text}")
                self.history = [] # Clear data on error
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching history from API: {e}")
            self.history = [] # Clear data on error
            
        self.update_tab_content() # Update UI after loading

    def add_user(self, e=None):
        # Hiển thị dialog thêm người dùng
        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()

        def save_user(e):
            # Xử lý lưu người dùng mới
            email = email_field.value
            username = new_username_field.value
            password = new_password_field.value
            confirm_password = confirm_password_field.value
            is_admin = is_admin_checkbox.value

            if not email or not username or not password or not confirm_password:
                error_text.value = "Vui lòng điền đầy đủ thông tin."
                self.page.update()
                return

            if password != confirm_password:
                error_text.value = "Mật khẩu xác nhận không khớp."
                self.page.update()
                return
            
            # Call API to add user
            if not self.token:
                print("Error: No token available for adding user.")
                error_text.value = "Lỗi xác thực."
                self.page.update()
                return

            try:
                headers = self.get_auth_header()
                response = requests.post(
                    f"{API_BASE_URL}/users/register",
                    json={
                        "email": email,
                        "username": username,
                        "password": password,
                        "is_admin": is_admin # API does not currently support setting is_admin on registration, need to update API if required
                    },
                    headers=headers
                )

                if response.status_code == 200:
                    print("User added successfully.")
                    self.load_users() # Reload user list
                    close_dlg(None) # Close dialog
                elif response.status_code == 400:
                     error_text.value = f"Lỗi: {response.json().get('detail', 'Email hoặc username đã tồn tại.')}"
                     self.page.update()
                elif response.status_code == 401:
                    print("Authentication failed during add user. Redirecting to login.")
                    self.page.go("/login")
                else:
                    error_text.value = f"Lỗi khi thêm người dùng: {response.status_code} - {response.text}"
                    self.page.update()
                    
            except requests.exceptions.RequestException as ex:
                error_text.value = f"Lỗi kết nối API khi thêm người dùng: {str(ex)}"
                self.page.update()
            except Exception as ex:
                 error_text.value = f"Lỗi không xác định khi thêm người dùng: {str(ex)}"
                 self.page.update()

        email_field = ft.TextField(label="Email", width=300)
        new_username_field = ft.TextField(label="Tên đăng nhập", width=300)
        new_password_field = ft.TextField(label="Mật khẩu", password=True, can_reveal_password=True, width=300)
        confirm_password_field = ft.TextField(label="Xác nhận mật khẩu", password=True, can_reveal_password=True, width=300)
        is_admin_checkbox = ft.Checkbox(label="Là Admin") # API currently doesn't support this on register

        error_text = ft.Text("", color=ft.Colors.RED)

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Thêm người dùng mới"),
            content=ft.Column(
                [
                    email_field,
                    new_username_field,
                    new_password_field,
                    confirm_password_field,
                    is_admin_checkbox,
                    error_text
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Hủy", on_click=close_dlg),
                ft.TextButton("Lưu", on_click=save_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def edit_user(self, user):
        print(f"Edit user clicked for user: {user.get('username', '')}") # Debug print
        # Hiển thị dialog chỉnh sửa người dùng
        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()

        def save_user(e):
            # Xử lý lưu thông tin người dùng
            updated_email = email_field.value
            updated_username = username_field.value
            updated_password = password_field.value
            updated_is_active = is_active_checkbox.value
            updated_is_admin = is_admin_checkbox.value

            update_data = {}
            if updated_email != user.get("email"):
                update_data["email"] = updated_email
            if updated_username != user.get("username"):
                update_data["username"] = updated_username
            if updated_password:
                # Only include password if it's not empty
                update_data["password"] = updated_password

            # Always send boolean values as they might change
            update_data["is_active"] = updated_is_active
            update_data["is_admin"] = updated_is_admin

            if not update_data:
                print("No changes to save.")
                close_dlg(None)
                return
                
            # Call API to update user
            if not self.token:
                print("Error: No token available for updating user.")
                error_text.value = "Lỗi xác thực."
                self.page.update()
                return
                
            try:
                headers = self.get_auth_header()
                user_id = user.get("id")
                response = requests.put(
                    f"{API_BASE_URL}/users/admin/{user_id}",
                    json=update_data,
                    headers=headers
                )

                if response.status_code == 200:
                    print(f"User {user_id} updated successfully.")
                    self.load_users() # Reload user list
                    close_dlg(None) # Close dialog
                elif response.status_code == 400:
                    error_text.value = f"Lỗi: {response.json().get('detail', 'Thông tin cập nhật không hợp lệ.')}"
                    self.page.update()
                elif response.status_code == 401:
                    print("Authentication failed during update user. Redirecting to login.")
                    self.page.go("/login")
                    close_dlg(None)
                elif response.status_code == 404:
                    print(f"User {user_id} not found.")
                    error_text.value = "Người dùng không tìm thấy."
                    self.page.update()
                    # Optionally, reload list in case user was deleted elsewhere
                    self.load_users()
                else:
                    error_text.value = f"Lỗi khi cập nhật người dùng {user_id}: {response.status_code} - {response.text}"
                    error_text.value = "Lỗi khi cập nhật người dùng."
                    self.page.update()
                    
            except requests.exceptions.RequestException as ex:
                error_text.value = f"Lỗi kết nối API khi cập nhật người dùng: {str(ex)}"
                self.page.update()
            except Exception as ex:
                 error_text.value = f"Lỗi không xác định khi cập nhật người dùng: {str(ex)}"
                 self.page.update()

        email_field = ft.TextField(label="Email", value=user.get("email", ""), width=300)
        username_field = ft.TextField(label="Tên đăng nhập", value=user.get("username", ""), width=300)
        password_field = ft.TextField(label="Mật khẩu mới (để trống nếu không đổi)", password=True, can_reveal_password=True, width=300)
        is_active_checkbox = ft.Checkbox(label="Hoạt động", value=user.get("is_active", True))
        is_admin_checkbox = ft.Checkbox(label="Là Admin", value=user.get("is_admin", False))

        error_text = ft.Text("", color=ft.Colors.RED)

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Chỉnh sửa người dùng: {user.get('username', '')}"),
            content=ft.Column(
                [
                    email_field,
                    username_field,
                    password_field,
                    is_active_checkbox,
                    is_admin_checkbox,
                    error_text
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Hủy", on_click=close_dlg),
                ft.TextButton("Lưu", on_click=save_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def delete_user(self, user):
        # Hiển thị dialog xác nhận xóa người dùng
        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()

        def confirm_delete(e):
            # Gọi API để xóa người dùng
            if not self.token:
                print("Error: No token available for deleting user.")
                # Optionally, redirect to login page
                # self.page.go("/login")
                close_dlg(None)
                return
                
            try:
                headers = self.get_auth_header()
                user_id = user.get("id")
                response = requests.delete(
                    f"{API_BASE_URL}/users/admin/{user_id}",
                    headers=headers
                )

                if response.status_code == 200:
                    print(f"User {user_id} deleted successfully.")
                    self.load_users() # Reload user list
                    close_dlg(None) # Close dialog
                elif response.status_code == 401:
                    print("Authentication failed during delete user. Redirecting to login.")
                    self.page.go("/login")
                    close_dlg(None)
                elif response.status_code == 404:
                    print(f"User {user_id} not found.")
                    # Optionally, show a message to the user
                    self.load_users() # Reload list in case user was already deleted
                    close_dlg(None)
                else:
                    print(f"Error deleting user {user_id}: {response.status_code} - {response.text}")
                    # Optionally, show an error message to the user
                    close_dlg(None)
                    
            except requests.exceptions.RequestException as ex:
                print(f"Error connecting to API when deleting user: {str(ex)}")
                # Optionally, show an error message to the user
                close_dlg(None)
            except Exception as ex:
                 print(f"Unknown error when deleting user: {str(ex)}")
                 # Optionally, show an error message to the user
                 close_dlg(None)

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Xác nhận xóa người dùng"),
            content=ft.Text(f"Bạn có chắc chắn muốn xóa người dùng {user.get('username', 'này')} không?"),
            actions=[
                ft.TextButton("Hủy", on_click=close_dlg),
                ft.TextButton("Xóa", on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def view_history_detail(self, history_item):
        # Hiển thị dialog chi tiết lịch sử
        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()

        # In a real app, you might fetch full details from API if needed
        # For now, just display the available details
        content = ft.Column(
            [
                ft.Text(f"ID: {history_item.get('id', '')}"),
                ft.Text(f"Người dùng ID: {history_item.get('user_id', '')}"), # Assuming user_id is available in admin history list
                ft.Text(f"Thời gian: {history_item.get('created_at', '')}"),
                ft.Text("Message:"),
                ft.Container(
                    content=ft.Text(history_item.get('message', ''), selectable=True),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    padding=10,
                    border_radius=5
                ),
                ft.Text("Response:"),
                 ft.Container(
                    content=ft.Text(history_item.get('response', ''), selectable=True),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    padding=10,
                    border_radius=5
                ),
                # Assuming image_path might be available or fetched
                ft.Text(f"Image Path: {history_item.get('image_path', 'N/A')}"),
            ],
            tight=True
        )

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Chi tiết lịch sử ID: {history_item.get('id', '')}"),
            content=ft.Container(content=content, width=500, padding=ft.padding.all(0)), # Set width for content container
            actions=[
                ft.TextButton("Đóng", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def delete_history(self, history_item):
        # Hiển thị dialog xác nhận xóa lịch sử
        def close_dlg(e):
            self.page.dialog.open = False
            self.page.update()

        def confirm_delete(e):
            # Gọi API để xóa lịch sử
            if not self.token:
                print("Error: No token available for deleting history.")
                # Optionally, redirect to login page
                # self.page.go("/login")
                close_dlg(None)
                return

            try:
                headers = self.get_auth_header()
                history_id = history_item.get("id")
                response = requests.delete(
                    f"{API_BASE_URL}/history/{history_id}",
                    headers=headers
                )

                if response.status_code == 200:
                    print(f"History item {history_id} deleted successfully.")
                    self.load_history() # Reload history list
                    close_dlg(None) # Close dialog
                elif response.status_code == 401:
                    print("Authentication failed during delete history. Redirecting to login.")
                    self.page.go("/login")
                    close_dlg(None)
                elif response.status_code == 404:
                    print(f"History item {history_id} not found.")
                    # Optionally, show a message to the user
                    self.load_history() # Reload list in case item was already deleted
                    close_dlg(None)
                elif response.status_code == 403:
                    print(f"Not enough permissions to delete history item {history_id}.")
                    # Optionally, show an error message to the user
                    close_dlg(None)
                else:
                    print(f"Error deleting history item {history_id}: {response.status_code} - {response.text}")
                    # Optionally, show an error message to the user
                    close_dlg(None)

            except requests.exceptions.RequestException as ex:
                print(f"Error connecting to API when deleting history: {str(ex)}")
                # Optionally, show an error message to the user
                close_dlg(None)
            except Exception as ex:
                 print(f"Unknown error when deleting history: {str(ex)}")
                 # Optionally, show an error message to the user
                 close_dlg(None)

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Xác nhận xóa lịch sử"),
            content=ft.Text(f"Bạn có chắc chắn muốn xóa mục lịch sử ID {history_item.get('id', '')} không?"),
            actions=[
                ft.TextButton("Hủy", on_click=close_dlg),
                ft.TextButton("Xóa", on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def logout_clicked(self, e):
        self.page.session.clear()
        self.page.go("/login")

if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Test Admin Page"
        page.session.set("username", "TestUserAdmin")
        page.session.set("token", "test_token")  # Thêm token giả để test
        admin_view = AdminPage(page)
        page.views.append(admin_view)
        page.update()
    ft.app(target=main)