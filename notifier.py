
try:
    from windows_toasts import Toast, WindowsToaster

    _toaster = WindowsToaster("宿舍电量监控")

    def send_toast(title: str, message: str) -> None:
        try:
            toast = Toast()
            toast.text_fields = [str(title), str(message)]
            _toaster.show_toast(toast)
            print("[通知] 已尝试发送：", title, message)
        except Exception as e:
            print("[通知失败]", e)

except Exception as e:
    def send_toast(title: str, message: str) -> None:
        print(f"[通知] {title}：{message}")
        print("[提示] windows-toasts 未成功加载：", e)