#!/usr/bin/env python3
"""
워크플로 생성 직접 테스트 스크립트
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 백엔드 앱 경로 추가
sys.path.append('/Users/jongho.jung/Desktop/jongho_project/PoC/local_ai_agent/backend')

async def test_workflow_creation():
    """워크플로 생성을 직접 테스트"""
    
    print("🧪 워크플로 생성 직접 테스트")
    print("=" * 50)
    
    try:
        # 앱 모듈 임포트
        from app.workflow_manager import workflow_manager
        from app.models.schemas import WorkflowCreateRequest
        
        print("✅ 모듈 임포트 성공")
        
        # 테스트 데이터
        test_data = WorkflowCreateRequest(
            user_input="할일 관리앱을 만들어줘. 할일 추가, 완료 체크, 삭제 기능이 필요해.",
            project_name="todo-app-test"
        )
        
        print(f"📝 테스트 데이터: {test_data}")
        
        # 워크플로 시작
        print("\n🚀 워크플로 시작...")
        workflow_id = await workflow_manager.start_workflow(test_data)
        print(f"✅ 워크플로 ID: {workflow_id}")
        
        # 상태 체크
        print("\n📊 상태 체크...")
        for i in range(5):
            status = await workflow_manager.get_workflow_status(workflow_id)
            print(f"상태 {i+1}: {json.dumps(status, indent=2, default=str, ensure_ascii=False)}")
            
            if status and status.get('status') in ['completed', 'failed']:
                break
                
            await asyncio.sleep(3)
        
        # 최종 상태
        final_status = await workflow_manager.get_workflow_status(workflow_id)
        print(f"\n🏁 최종 상태: {json.dumps(final_status, indent=2, default=str, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow_creation())
