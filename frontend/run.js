#!/usr/bin/env node

/**
 * 멀티 AI 에이전트 웹서비스 생성 시스템 - Frontend 실행 스크립트
 * 
 * 이 스크립트는 다음을 수행합니다:
 * 1. Node.js 및 npm 버전 확인
 * 2. package.json 의존성 설치 확인
 * 3. 환경변수 설정 확인
 * 4. Vite 개발 서버 실행
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// 색상 출력을 위한 ANSI 코드
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkNodeVersion() {
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
  
  log('📋 Node.js 환경 확인 중...', 'blue');
  log(`✅ Node.js: ${nodeVersion}`, 'green');
  
  if (majorVersion < 16) {
    log('❌ Node.js 16 이상이 필요합니다.', 'red');
    process.exit(1);
  }
}

function checkCurrentDirectory() {
  const currentDir = path.basename(process.cwd());
  if (currentDir !== 'frontend') {
    log('❌ 이 스크립트는 frontend 디렉토리에서 실행해야 합니다.', 'red');
    log(`현재 위치: ${process.cwd()}`, 'red');
    log('실행 방법: cd frontend && node run.js', 'yellow');
    process.exit(1);
  }
}

function checkPackageJson() {
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    log('❌ package.json 파일을 찾을 수 없습니다.', 'red');
    process.exit(1);
  }
  
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  log(`✅ 프로젝트: ${packageJson.name || 'Unknown'}`, 'green');
  return packageJson;
}

function checkNodeModules() {
  const nodeModulesPath = path.join(process.cwd(), 'node_modules');
  if (!fs.existsSync(nodeModulesPath)) {
    log('📦 node_modules가 없습니다. npm install을 실행합니다...', 'yellow');
    return false;
  }
  log('✅ node_modules 확인됨', 'green');
  return true;
}

function installDependencies() {
  return new Promise((resolve, reject) => {
    log('📦 의존성 설치 중...', 'blue');
    
    const npm = spawn('npm', ['install'], {
      stdio: 'inherit',
      shell: true
    });
    
    npm.on('close', (code) => {
      if (code === 0) {
        log('✅ 의존성 설치 완료', 'green');
        resolve();
      } else {
        log('❌ 의존성 설치 실패', 'red');
        reject(new Error(`npm install failed with code ${code}`));
      }
    });
    
    npm.on('error', (error) => {
      log(`❌ npm install 실행 중 오류: ${error.message}`, 'red');
      reject(error);
    });
  });
}

function startDevelopmentServer() {
  return new Promise((resolve, reject) => {
    log('🚀 Frontend 개발 서버를 시작합니다...', 'blue');
    log('📍 URL: http://localhost:3025', 'cyan');
    log('🔗 Backend API 연결: http://localhost:8025', 'cyan');
    log('⏹️  중지하려면 Ctrl+C를 누르세요', 'yellow');
    log('', 'reset');
    
    const vite = spawn('npm', ['run', 'dev'], {
      stdio: 'inherit',
      shell: true
    });
    
    vite.on('close', (code) => {
      if (code === 0) {
        log('\n🛑 Frontend 서버가 정상적으로 종료되었습니다.', 'green');
        resolve();
      } else {
        log(`\n❌ Frontend 서버가 오류로 종료되었습니다. (코드: ${code})`, 'red');
        reject(new Error(`Development server failed with code ${code}`));
      }
    });
    
    vite.on('error', (error) => {
      log(`❌ 개발 서버 실행 중 오류: ${error.message}`, 'red');
      reject(error);
    });
    
    // Graceful shutdown
    process.on('SIGINT', () => {
      log('\n🛑 종료 신호를 받았습니다. 서버를 중지합니다...', 'yellow');
      vite.kill('SIGINT');
    });
    
    process.on('SIGTERM', () => {
      log('\n🛑 종료 신호를 받았습니다. 서버를 중지합니다...', 'yellow');
      vite.kill('SIGTERM');
    });
  });
}

async function main() {
  try {
    log('🎯 멀티 AI 에이전트 웹서비스 생성 시스템 - Frontend', 'magenta');
    log('', 'reset');
    
    // 1. 환경 확인
    checkNodeVersion();
    checkCurrentDirectory();
    checkPackageJson();
    
    // 2. 의존성 확인 및 설치
    const hasNodeModules = checkNodeModules();
    if (!hasNodeModules) {
      await installDependencies();
    }
    
    // 3. 개발 서버 시작
    await startDevelopmentServer();
    
  } catch (error) {
    log(`❌ Frontend 실행 중 오류 발생: ${error.message}`, 'red');
    process.exit(1);
  }
}

// 스크립트가 직접 실행될 때만 main 함수 호출
if (require.main === module) {
  main();
}

module.exports = {
  main,
  checkNodeVersion,
  checkCurrentDirectory,
  checkPackageJson,
  checkNodeModules,
  installDependencies,
  startDevelopmentServer
};
