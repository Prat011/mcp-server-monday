#!/usr/bin/env python3
"""
Integration test for monday-update-item-name functionality.
Tests the actual function that will be used in the Docker container.
"""

import asyncio
import json
import os
from monday import MondayClient

# Import the actual function we're testing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from mcp_server_monday.item import handle_monday_update_item_name


async def test_update_item_name():
    """Test the monday-update-item-name function with real API calls"""
    
    # Get Monday.com credentials from environment
    api_key = os.getenv('MONDAY_API_KEY')
    if not api_key:
        print("❌ MONDAY_API_KEY environment variable not set")
        return False
    
    # Initialize Monday.com client
    monday_client = MondayClient(api_key)
    
    # Test parameters - use your actual board data
    test_params = {
        "boardId": "9424670402",
        "groupId": "topics", 
        "itemName": "McpTest",
        "statusValue": "Done"
    }
    
    print(f"🧪 Testing monday-update-item-name with params:")
    print(f"   Board ID: {test_params['boardId']}")
    print(f"   Group ID: {test_params['groupId']}")
    print(f"   Item Name: {test_params['itemName']}")
    print(f"   Status Value: {test_params['statusValue']}")
    print()
    
    try:
        # Call the actual function
        result = await handle_monday_update_item_name(
            boardId=test_params["boardId"],
            groupId=test_params["groupId"],
            itemName=test_params["itemName"],
            statusValue=test_params["statusValue"],
            monday_client=monday_client
        )
        
        # Check result
        if result and len(result) > 0:
            response_text = result[0].text
            
            if "Error" in response_text:
                print(f"❌ Function returned error: {response_text}")
                return False
            else:
                print(f"✅ Function succeeded: {response_text}")
                return True
        else:
            print("❌ Function returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("=== Monday.com Update Item Name Integration Test ===")
    print()
    
    # Run the test
    success = await test_update_item_name()
    
    print()
    if success:
        print("🎉 All tests passed! Function is working correctly.")
        print("✅ Ready for Docker build")
    else:
        print("💥 Tests failed! Fix issues before Docker build")
        print("❌ Not ready for Docker build")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
