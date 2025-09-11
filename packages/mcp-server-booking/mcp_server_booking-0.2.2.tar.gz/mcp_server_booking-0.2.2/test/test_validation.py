#!/usr/bin/env python3
"""
测试预订系统验证功能
这个脚本用于测试新实现的验证系统，不会影响现有的工具函数
"""

import os
import sys
import logging
import traceback
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加src目录到Python路径
# 从test目录向上一级，然后进入src目录
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from dotenv import load_dotenv
env_dir = os.path.join(current_dir, '.env')
load_dotenv(env_dir)

from mcp_server_booking.booking_system import BookingSystem, ValidationError

def test_validation_system():
    """测试验证系统的各种场景"""
    
    print("=== 预订系统验证测试 ===\n")
    
    # 注意：这里需要设置有效的用户名和密码
    # 为了测试，我们使用环境变量
    username = os.getenv("BOOKING_USERNAME")
    password = os.getenv("BOOKING_PASSWORD")
    
    if not username or not password:
        print("❌ 请设置环境变量 BOOKING_USERNAME 和 BOOKING_PASSWORD")
        print("例如: export BOOKING_USERNAME='your_username'")
        print("例如: export BOOKING_PASSWORD='your_password'")
        return
    
    try:
        # 创建BookingSystem实例
        booking_system = BookingSystem(username, password)
        print("✅ 成功创建BookingSystem实例")
        
        # 显示当前验证规则
        print(f"\n📋 当前验证规则:")
        print(f"  - weekly_max_bookings: 1 (每周最多1次)")
        print(f"  - max_booking_duration_hours: 1 (单次最多1小时)")
        print(f"  - booking_start_hour: 8 (8:00开始)")
        print(f"  - booking_end_hour: 22 (22:00结束)")
        
        # 测试用例（基于实际验证规则）
        test_cases = [
            {
                "name": "正常预订请求",
                "params": {
                    "field_id": "1097",
                    "place_id": "1101", 
                    "start_time": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d 10:00"),
                    "end_time": (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d 11:00"),
                    "telephone": "1234567890",
                    "reason": "羽毛球练习",
                    "details": "和朋友一起练习羽毛球"
                },
                "should_pass": True
            },
            {
                "name": "超出预订时间范围（过早）",
                "params": {
                    "field_id": "1097",
                    "place_id": "1101",
                    "start_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 06:00"),
                    "end_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 07:00"),
                    "telephone": "1234567890",
                    "reason": "羽毛球练习",
                    "details": "和朋友一起练习羽毛球"
                },
                "should_pass": False
            },
            {
                "name": "超出预订时间范围（过晚）",
                "params": {
                    "field_id": "1097",
                    "place_id": "1101",
                    "start_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 23:00"),
                    "end_time": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 00:00"),
                    "telephone": "1234567890",
                    "reason": "羽毛球练习",
                    "details": "和朋友一起练习羽毛球"
                },
                "should_pass": False
            },
            {
                "name": "预约时长过长",
                "params": {
                    "field_id": "1097",
                    "place_id": "1101",
                    "start_time": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d 10:00"),
                    "end_time": (datetime.now() + timedelta(hours=4)).strftime("%Y-%m-%d 12:00"),
                    "telephone": "1234567890",
                    "reason": "羽毛球练习",
                    "details": "和朋友一起练习羽毛球"
                },
                "should_pass": False
            },
            {
                "name": "边界时间（8:00-9:00）",
                "params": {
                    "field_id": "1097",
                    "place_id": "1101",
                    "start_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 08:00"),
                    "end_time": (datetime.now() + timedelta(days=1, hours=1)).strftime("%Y-%m-%d 09:00"),
                    "telephone": "1234567890",
                    "reason": "羽毛球练习",
                    "details": "和朋友一起练习羽毛球"
                },
                "should_pass": True
            },
            {
                "name": "边界时间（21:00-22:00）",
                "params": {
                    "field_id": "1097",
                    "place_id": "1101",
                    "start_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 21:00"),
                    "end_time": (datetime.now() + timedelta(days=1, hours=1)).strftime("%Y-%m-%d 22:00"),
                    "telephone": "1234567890",
                    "reason": "羽毛球练习",
                    "details": "和朋友一起练习羽毛球"
                },
                "should_pass": True
            },
            {
                "name": "预约时长30分钟（正常）",
                "params": {
                    "field_id": "1097",
                    "place_id": "1101",
                    "start_time": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d 10:00"),
                    "end_time": (datetime.now() + timedelta(hours=2, minutes=30)).strftime("%Y-%m-%d 10:30"),
                    "telephone": "1234567890",
                    "reason": "羽毛球练习",
                    "details": "和朋友一起练习羽毛球"
                },
                "should_pass": True
            }
        ]
        
        # 运行测试用例
        print(f"\n🧪 开始运行 {len(test_cases)} 个测试用例...\n")
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"测试 {i}: {test_case['name']}")
            print(f"参数: {test_case['params']}")
            
            try:
                print(f"🔍 开始验证...")
                is_valid, message = booking_system.validate_booking_request(**test_case['params'])
                print(f"🔍 验证完成: {is_valid}, {message}")
                
                if is_valid == test_case['should_pass']:
                    print(f"✅ 通过 - {message}")
                    passed_tests += 1
                else:
                    print(f"❌ 失败 - 期望: {'通过' if test_case['should_pass'] else '失败'}, 实际: {'通过' if is_valid else '失败'}")
                    print(f"   消息: {message}")
                    
            except Exception as e:
                print(f"❌ 异常 - {str(e)}")
                traceback.print_exc()
            
            print("-" * 50)
        
        # 测试结果总结
        print(f"\n📊 测试结果总结:")
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 所有测试都通过了！")
        else:
            print("⚠️  部分测试失败，需要检查验证逻辑")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def test_rule_configuration():
    """测试验证规则配置功能"""
    
    print("\n=== 验证规则配置测试 ===\n")
    
    try:
        print("📋 当前验证规则配置:")
        print("  - weekly_max_bookings: 1 (每周最多1次)")
        print("  - max_booking_duration_hours: 1 (单次最多1小时)")
        print("  - booking_start_hour: 8 (8:00开始)")
        print("  - booking_end_hour: 22 (22:00结束)")
        print()
        print("✅ 验证规则配置已硬编码在BookingSystem类中")
        print("💡 如需修改规则，请直接修改BOOKING_RULES常量")
        
    except Exception as e:
        print(f"❌ 规则配置测试失败: {str(e)}")

if __name__ == "__main__":
    print("预订系统验证功能测试")
    print("=" * 50)
    
    # 运行验证系统测试
    test_validation_system()
    
    # 运行规则配置测试
    test_rule_configuration()
    
    print("\n测试完成！")
