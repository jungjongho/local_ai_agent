#!/bin/bash

# Test script for AI Agent Tool Usage

echo "🤖 Testing AI Agent Tool Usage"
echo "================================"

echo ""
echo "1. Testing basic file creation..."
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "data/workspace 경로에 '안녕'이 적혀있는 hello.txt 파일을 만들어주세요"
      }
    ]
  }' | jq '.'

echo ""
echo "2. Testing file reading..."
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "방금 만든 hello.txt 파일의 내용을 읽어서 보여주세요"
      }
    ]
  }' | jq '.'

echo ""
echo "3. Testing web search..."
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Python programming에 대해 웹에서 검색해주세요"
      }
    ]
  }' | jq '.'

echo ""
echo "4. Testing combined operations..."
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "AI 최신 뉴스를 검색해서 요약한 내용을 news_summary.txt 파일로 저장해주세요"
      }
    ]
  }' | jq '.'

echo ""
echo "✅ Test completed!"
