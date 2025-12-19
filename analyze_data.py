"""
GMGN 用户数据分析工具
分析已抓取的用户数据，生成统计报告
"""
import json
from pathlib import Path
from collections import Counter

def analyze_users(json_file='gmgn_users_dedup.json'):
    """分析用户数据"""
    json_path = Path(json_file)

    if not json_path.exists():
        print(f"错误: 文件 {json_file} 不存在")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    users = data.get('users', [])
    total_users = len(users)

    print("=" * 60)
    print("GMGN 用户数据分析报告")
    print("=" * 60)
    print(f"数据文件: {json_path.absolute()}")
    print(f"最后更新: {data.get('last_updated', 'N/A')}")
    print(f"总用户数: {total_users}\n")

    if total_users == 0:
        print("没有数据可分析")
        return

    # 统计标签分布
    all_tags = []
    for user in users:
        all_tags.extend(user.get('user_tags', []))

    tag_counter = Counter(all_tags)

    print("📊 用户标签分布:")
    print("-" * 60)
    for tag, count in tag_counter.most_common():
        percentage = (count / total_users) * 100
        print(f"  {tag:20s} {count:6d} 个用户 ({percentage:.1f}%)")

    # 统计粉丝数
    followers_list = [user.get('followers', 0) for user in users]
    avg_followers = sum(followers_list) / len(followers_list) if followers_list else 0
    max_followers = max(followers_list) if followers_list else 0
    min_followers = min(followers_list) if followers_list else 0

    print(f"\n📈 粉丝数统计:")
    print("-" * 60)
    print(f"  平均粉丝数: {avg_followers:.0f}")
    print(f"  最多粉丝数: {max_followers}")
    print(f"  最少粉丝数: {min_followers}")

    # Top 10 粉丝最多的用户
    top_users = sorted(users, key=lambda x: x.get('followers', 0), reverse=True)[:10]

    print(f"\n🏆 Top 10 粉丝最多的用户:")
    print("-" * 60)
    for i, user in enumerate(top_users, 1):
        handle = user.get('handle', 'N/A')
        followers = user.get('followers', 0)
        tags = ', '.join(user.get('user_tags', []))
        print(f"  {i:2d}. @{handle:20s} {followers:6d} 粉丝 [{tags}]")

    # 统计平台分布
    platform_counter = Counter([user.get('platform', 0) for user in users])

    print(f"\n🌐 平台分布:")
    print("-" * 60)
    for platform, count in platform_counter.most_common():
        platform_name = "Twitter" if platform == 0 else f"Platform {platform}"
        percentage = (count / total_users) * 100
        print(f"  {platform_name:20s} {count:6d} 个用户 ({percentage:.1f}%)")

    # 按标签分组的Top用户
    print(f"\n📋 按标签分类的热门用户:")
    print("-" * 60)
    for tag, _ in tag_counter.most_common(5):  # 只显示前5个标签
        tag_users = [u for u in users if tag in u.get('user_tags', [])]
        tag_users.sort(key=lambda x: x.get('followers', 0), reverse=True)
        top_tag_users = tag_users[:3]  # 每个标签显示前3个用户

        print(f"\n  [{tag}] - {len(tag_users)} 个用户")
        for i, user in enumerate(top_tag_users, 1):
            handle = user.get('handle', 'N/A')
            followers = user.get('followers', 0)
            print(f"    {i}. @{handle:20s} {followers:6d} 粉丝")

    print("\n" + "=" * 60)

def export_by_tag(json_file='gmgn_users_dedup.json', output_dir='exports'):
    """按标签导出用户数据"""
    json_path = Path(json_file)

    if not json_path.exists():
        print(f"错误: 文件 {json_file} 不存在")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    users = data.get('users', [])
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 按标签分组
    tag_groups = {}
    for user in users:
        for tag in user.get('user_tags', []):
            if tag not in tag_groups:
                tag_groups[tag] = []
            tag_groups[tag].append(user)

    # 导出每个标签
    for tag, tag_users in tag_groups.items():
        tag_users.sort(key=lambda x: x.get('followers', 0), reverse=True)

        output_file = output_path / f"{tag}_users.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'tag': tag,
                'total_users': len(tag_users),
                'users': tag_users
            }, f, ensure_ascii=False, indent=2)

        print(f"✅ 导出 {tag}: {len(tag_users)} 个用户 -> {output_file}")

    print(f"\n所有标签已导出到: {output_path.absolute()}")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        json_file = sys.argv[2] if len(sys.argv) > 2 else 'gmgn_users_dedup.json'

        if command == 'analyze':
            analyze_users(json_file)
        elif command == 'export':
            export_by_tag(json_file)
        else:
            print("用法:")
            print("  python analyze_data.py analyze [json_file]  - 分析数据")
            print("  python analyze_data.py export [json_file]   - 按标签导出")
    else:
        # 默认执行分析
        analyze_users()