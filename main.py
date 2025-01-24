import os
import subprocess

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
    print("iptables 初始化完成！")

def add_iptables_rule():
    """添加一条 iptables 规则。"""
    rule = input("请输入 iptables 规则：")
    run_command(f"iptables {rule}")
    print("规则已添加！")

def save_iptables():
    """保存 iptables 规则。"""
    run_command("/iptables_rule/unlock_iptables_edit")
    run_command("iptables-save > /iptables_rule/iptables_acl")
    run_command("/iptables_rule/lock_iptables_edit")
    print("规则已保存！")

def configure_firewall():
    """重新加载防火墙规则。"""
    run_command("firewall-cmd --reload")
    print("防火墙规则已重新加载！")

def view_policies():
    """查看当前生效的防火墙或 iptables 策略。"""
    if check_firewall_status():
        print(run_command("firewall-cmd --list-all"))
    else:
        print(run_command("iptables -L -n"))

def iptables_menu():
    """iptables 操作菜单。"""
    while True:
        print("\n=== iptables 控制面板 ===")
        print("1. 初始化 iptables")
        print("2. 添加 iptables 规则")
        print("3. 保存 iptables 规则")
        print("4. 返回主菜单")
        choice = input("请选择操作：")
        if choice == "1":
            initialize_iptables()
        elif choice == "2":
            add_iptables_rule()
        elif choice == "3":
            save_iptables()
        elif choice == "4":
            break
        else:
            print("无效的选择，请重试！")

def firewall_menu():
    """firewall 操作菜单。"""
    while True:
        print("\n=== firewall 控制面板 ===")
        print("1. 配置防火墙")
        print("2. 查看防火墙策略")
        print("3. 返回主菜单")
        choice = input("请选择操作：")
        if choice == "1":
            configure_firewall()
        elif choice == "2":
            view_policies()
        elif choice == "3":
            break
        else:
            print("无效的选择，请重试！")

def main_menu():
    """主菜单。"""
    while True:
        print("\n=== 防火墙和 iptables 控制面板 ===")
        status = "firewall" if check_firewall_status() else "iptables"
        print(f"当前生效策略: {status}")
        print("1. iptables 操作" if not check_firewall_status() else "", end="")
        print("\n2. firewall 操作")
        print("3. 查看当前策略")
        print("4. 退出")
        choice = input("请选择操作：")
        if choice == "1" and not check_firewall_status():
            iptables_menu()
        elif choice == "2":
            firewall_menu()
        elif choice == "3":
            view_policies()
        elif choice == "4":
            print("程序已退出。")
            break
        else:
            print("无效的选择，请重试！")

if __name__ == "__main__":
    main_menu()
