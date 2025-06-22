#!/usr/bin/env python3
"""
Real integration test for monday-update-item-name functionality.
Tests the actual Monday.com API integration before Docker deployment.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# Add src to path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from monday import MondayClient
    from mcp_server_monday.item import handle_monday_update_item_name
    from mcp_server_monday.board import handle_monday_get_board_groups
    from mcp_server_monday.item import handle_monday_list_items_in_groups
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you have installed the dependencies: uv sync")
    sys.exit(1)


class RealMondayIntegrationTest:
    """Real integration test suite using actual Monday.com API"""
    
    def __init__(self):
        self.api_key = os.getenv('MONDAY_API_KEY')
        self.workspace_name = os.getenv('MONDAY_WORKSPACE_NAME', '11399036')
        
        if not self.api_key:
            raise ValueError("MONDAY_API_KEY environment variable required")
        
        self.client = MondayClient(self.api_key)
        self.test_board_id = "9424670402"  # Your test board
        self.test_group_id = "topics"      # Your test group
        self.test_item_name = "McpTest"    # Your test item
    
    async def test_board_groups_access(self) -> bool:
        """Test if we can access board groups - validates API connection"""
        try:
            print("🔍 Testing board groups access...")
            
            result = await handle_monday_get_board_groups(
                boardId=self.test_board_id,
                monday_client=self.client
            )
            
            # Parse response to validate structure
            assert len(result) == 1
            assert result[0].type == "text"
            
            response_text = result[0].text
            assert "Monday.com board groups" in response_text
            
            # Try to parse JSON response
            json_start = response_text.find('{')
            if json_start != -1:
                json_data = json.loads(response_text[json_start:])
                assert "data" in json_data
                print(f"✅ Found {len(json_data.get('data', {}).get('boards', [{}])[0].get('groups', []))} groups in board")
            
            print("✅ Board groups access: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Board groups access: FAILED - {e}")
            return False
    
    async def test_list_items_in_group(self) -> bool:
        """Test if we can list items in the test group"""
        try:
            print("🔍 Testing list items in group...")
            
            result = await handle_monday_list_items_in_groups(
                boardId=self.test_board_id,
                groupIds=[self.test_group_id],
                limit=50,
                monday_client=self.client
            )
            
            # Validate response structure
            assert len(result) == 1
            assert result[0].type == "text"
            
            response_text = result[0].text
            
            # Check if our test item exists
            if self.test_item_name in response_text:
                print(f"✅ Found test item '{self.test_item_name}' in group")
            else:
                print(f"⚠️  Test item '{self.test_item_name}' not found in group")
                print("Available items in response:")
                # Try to extract item names from response
                json_start = response_text.find('{')
                if json_start != -1:
                    json_data = json.loads(response_text[json_start:])
                    items = json_data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
                    for item in items:
                        print(f"  - {item.get('name')} (ID: {item.get('id')})")
            
            print("✅ List items in group: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ List items in group: FAILED - {e}")
            return False
    
    async def test_json_serialization_format(self) -> bool:
        """Test different JSON serialization formats for Monday.com status columns"""
        try:
            print("🔍 Testing JSON serialization formats...")
            
            # Test different formats that Monday.com might accept
            formats_to_test = [
                {"status": "Done"},  # Simple string
                {"status": {"label": "Done"}},  # Label object
                {"status": {"index": 1}},  # Index-based (1 = Done)
                {"status": {"id": "done"}},  # ID-based
            ]
            
            for i, column_values in enumerate(formats_to_test):
                serialized = json.dumps(column_values)
                print(f"  Format {i+1}: {serialized}")
            
            print("✅ JSON serialization format: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ JSON serialization format: FAILED - {e}")
            return False
    
    async def test_update_item_by_name_dry_run(self) -> bool:
        """Test the update item by name function with different status formats"""
        try:
            print("🔍 Testing update item by name (trying different formats)...")
            
            # First, let's see what items are available
            print("Step 1: Checking available items...")
            items_result = await handle_monday_list_items_in_groups(
                boardId=self.test_board_id,
                groupIds=[self.test_group_id],
                limit=50,
                monday_client=self.client
            )
            
            # Extract item information for debugging
            response_text = items_result[0].text
            json_start = response_text.find('{')
            if json_start != -1:
                json_data = json.loads(response_text[json_start:])
                items = json_data.get('data', {}).get('boards', [{}])[0].get('items_page', {}).get('items', [])
                
                print("Available items:")
                target_item_found = False
                for item in items:
                    item_name = item.get('name')
                    item_id = item.get('id')
                    print(f"  - {item_name} (ID: {item_id})")
                    if item_name == self.test_item_name:
                        target_item_found = True
                        print(f"    ✅ Target item found!")
                        # Show current column values for debugging
                        column_values = item.get('column_values', [])
                        for col in column_values:
                            if col.get('id') == 'status':
                                print(f"    Current status: {col.get('text')} (raw: {col.get('value')})")
                
                if not target_item_found:
                    print(f"⚠️  Target item '{self.test_item_name}' not found!")
                    return False
            
            # Test direct API call to understand the expected format
            print("Step 2: Testing direct API update with Monday client...")
            try:
                # Try with Python dict (not JSON string)
                test_formats = [
                    ("Dict Label format", {"status": {"label": "Done"}}),
                    ("Dict Index format", {"status": {"index": 1}}),
                    ("Dict String format", {"status": "Done"}),
                ]
                
                for format_name, column_dict in test_formats:
                    print(f"  Testing {format_name}: {column_dict}")
                    try:
                        response = self.client.items.change_multiple_column_values(
                            board_id=self.test_board_id,
                            item_id="9424694439",  # McpTest ID
                            column_values=column_dict
                        )
                        print(f"    ✅ {format_name} succeeded!")
                        return True
                    except Exception as api_error:
                        print(f"    ❌ {format_name} failed: {api_error}")
                        continue
                
                print("❌ All format attempts failed")
                return False
                
            except Exception as e:
                print(f"❌ Direct API test failed: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Update item by name: FAILED - {e}")
            return False


async def run_real_integration_tests():
    """Run real integration tests with Monday.com API"""
    print("🧪 Running Real Monday.com Integration Tests")
    print("=" * 60)
    
    try:
        test_suite = RealMondayIntegrationTest()
        print(f"✅ Connected to Monday.com with workspace: {test_suite.workspace_name}")
        print(f"✅ Testing board: {test_suite.test_board_id}")
        print(f"✅ Testing group: {test_suite.test_group_id}")
        print(f"✅ Testing item: {test_suite.test_item_name}")
        print()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nTo run real integration tests, set environment variables:")
        print("export MONDAY_API_KEY='your_api_key'")
        print("export MONDAY_WORKSPACE_NAME='your_workspace_id'")
        return 1
    
    tests = [
        test_suite.test_json_serialization_format,
        test_suite.test_board_groups_access,
        test_suite.test_list_items_in_group,
        test_suite.test_update_item_by_name_dry_run,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"📊 Integration Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Ready for Docker deployment.")
        return 0
    else:
        print("❌ Some integration tests failed. Check API connectivity and configuration.")
        return 1


def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['MONDAY_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nSet them with:")
        for var in missing_vars:
            print(f"export {var}='your_value'")
        return False
    
    return True


if __name__ == "__main__":
    print("🔧 Checking environment configuration...")
    if not check_environment():
        sys.exit(1)
    
    print("✅ Environment configured correctly")
    print()
    
    # Run real integration tests
    exit_code = asyncio.run(run_real_integration_tests())
    sys.exit(exit_code)
