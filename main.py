import os
import subprocess
import curses

def run_command(command):
    """运行 shell 命令并返回其输出。"""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"错误: {e.stderr.strip()}"

def check_firewall_status():
    """检查防火墙是否处于开启状态。"""
    status = run_command("systemctl is-active firewalld")
    return status == "active"

def initialize_iptables():
    """初始化 iptables 规则框架。"""
    os.makedirs("/iptables_rule", exist_ok=True)
    with open("/iptables_rule/iptables_acl", "w") as f:
        f.write("")
    commands = [
        "touch /iptables_rule/lock_iptables_edit",
        "touch /iptables_rule/unlock_iptables_edit",
        "echo 'chattr +i iptables_acl' > /iptables_rule/lock_iptables_edit",
        "echo 'chattr -i iptables_acl' > /iptables_rule/unlock_iptables_edit",
        "chmod +x /iptables_rule/lock_iptables_edit",
        "chmod +x /iptables_rule/unlock_iptables_edit",
        "chattr +i /iptables_rule/unlock_iptables_edit",
        "chattr +i /iptables_rule/lock_iptables_edit",
        "chattr +i /iptables_rule/iptables_acl",
    ]
    for cmd in commands:
        run_command(cmd)

def add_iptables_rule(rule):
    """添加一条 iptables 规则。"""
    run_command(f"iptables {rule}")

def save_iptables():
    """保存 iptables 规则。"""
    run_command("/iptables_rule/unlock_iptables_edit")
    run_command("iptables-save > /iptables_rule/iptables_acl")
    run_command("/iptables_rule/lock_iptables_edit")

def configure_firewall():
    """重新加载防火墙规则。"""
    run_command("firewall-cmd --reload")

def view_policies():
    """查看当前生效的防火墙或 iptables 策略。"""
    if check_firewall_status():
        return run_command("firewall-cmd --list-all")
    else:
        return run_command("iptables -L -n")

def iptables_menu(stdscr):
    """显示 iptables 菜单。"""
    curses.curs_set(0)
    current_row = 0
    menu = [
        "初始化 iptables",
        "添加 iptables 规则",
        "保存 iptables 规则",
        "返回主菜单",
    ]

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "iptables 控制面板", curses.A_BOLD)
        for idx, row in enumerate(menu):
            x = 0
            y = idx + 1
            if idx == current_row:
                stdscr.addstr(y, x, row, curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(menu) - 1:  # 返回主菜单
                break
            elif current_row == 0:  # 初始化 iptables
                initialize_iptables()
            elif current_row == 1:  # 添加 iptables 规则
                stdscr.clear()
                stdscr.addstr(0, 0, "请输入 iptables 规则:")
                curses.echo()
                rule = stdscr.getstr(1, 0).decode("utf-8")
                add_iptables_rule(rule)
                curses.noecho()
            elif current_row == 2:  # 保存 iptables 规则
                save_iptables()

        stdscr.refresh()

def firewall_menu(stdscr):
    """显示 firewall 菜单。"""
    curses.curs_set(0)
    current_row = 0
    menu = [
        "配置防火墙",
        "查看防火墙策略",
        "返回主菜单",
    ]

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "firewall 控制面板", curses.A_BOLD)
        for idx, row in enumerate(menu):
            x = 0
            y = idx + 1
            if idx == current_row:
                stdscr.addstr(y, x, row, curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(menu) - 1:  # 返回主菜单
                break
            elif current_row == 0:  # 配置防火墙
                configure_firewall()
            elif current_row == 1:  # 查看防火墙策略
                stdscr.clear()
                policies = view_policies()
                stdscr.addstr(0, 0, policies)
                stdscr.refresh()
                stdscr.getch()

        stdscr.refresh()

def main_menu(stdscr):
    """显示主菜单。"""
    curses.curs_set(0)
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "防火墙和 iptables 控制面板", curses.A_BOLD)
        status = "firewall" if check_firewall_status() else "iptables"
        stdscr.addstr(1, 0, f"当前生效策略: {status}", curses.A_BOLD)

        menu = [
            "iptables 操作" if not check_firewall_status() else None,
            "firewall 操作",
            "查看当前策略",
            "退出",
        ]
        menu = [item for item in menu if item]

        for idx, row in enumerate(menu):
            x = 0
            y = idx + 2
            if idx == current_row:
                stdscr.addstr(y, x, row, curses.color_pair(1))
            else:
                stdscr.addstr(y, x, row)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == len(menu) - 1:  # 退出
                break
            elif menu[current_row] == "iptables 操作":
                curses.wrapper(iptables_menu)
            elif menu[current_row] == "firewall 操作":
                curses.wrapper(firewall_menu)
            elif menu[current_row] == "查看当前策略":
                policies = view_policies()
                stdscr.clear()
                stdscr.addstr(0, 0, policies)
                stdscr.refresh()
                stdscr.getch()

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main_menu)
