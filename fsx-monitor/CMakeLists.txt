cmake_minimum_required(VERSION 3.20)

project(fsx_monitor LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT WIN32)
  message(WARNING "This project targets Windows (FSX:SE). Build on Windows with the SimConnect SDK installed. Stubs will build on non-Windows but do nothing.")
endif()

option(ENABLE_SIMCONNECT "Enable SimConnect integration" ON)
option(ENABLE_FSUIPC "Enable FSUIPC integration" ON)

# Optional: specify the SimConnect SDK root (where SimConnect.h and SimConnect.lib reside)
set(SIMCONNECT_SDK_DIR "" CACHE PATH "Path to SimConnect SDK root (contains include/ and lib/).")
set(FSUIPC_SDK_DIR "" CACHE PATH "Path to FSUIPC Client SDK root (contains headers and libs).")

add_executable(fsx_monitor
  src/main.cpp
  src/Logger.cpp
  src/Config.cpp
  src/SimConnectMonitor.cpp
  src/FSUIPCMonitor.cpp
)

target_include_directories(fsx_monitor PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

if(WIN32 AND ENABLE_SIMCONNECT)
  if(SIMCONNECT_SDK_DIR)
    target_include_directories(fsx_monitor PRIVATE ${SIMCONNECT_SDK_DIR}/include)
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
      target_link_directories(fsx_monitor PRIVATE ${SIMCONNECT_SDK_DIR}/lib/x64)
    else()
      target_link_directories(fsx_monitor PRIVATE ${SIMCONNECT_SDK_DIR}/lib)
    endif()
    target_link_libraries(fsx_monitor PRIVATE SimConnect)
    target_compile_definitions(fsx_monitor PRIVATE FSX_SIMCONNECT_ENABLED=1)
  else()
    message(WARNING "SIMCONNECT_SDK_DIR not set. SimConnect will be disabled.")
  endif()
endif()

if(WIN32 AND ENABLE_FSUIPC)
  if(FSUIPC_SDK_DIR)
    target_include_directories(fsx_monitor PRIVATE ${FSUIPC_SDK_DIR}/Include ${FSUIPC_SDK_DIR}/SDK/Inc ${FSUIPC_SDK_DIR})
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
      target_link_directories(fsx_monitor PRIVATE ${FSUIPC_SDK_DIR}/Library ${FSUIPC_SDK_DIR}/Lib ${FSUIPC_SDK_DIR}/Lib64)
    else()
      target_link_directories(fsx_monitor PRIVATE ${FSUIPC_SDK_DIR}/Library ${FSUIPC_SDK_DIR}/Lib)
    endif()
    # Common lib names from FSUIPC SDK distributions
    find_library(FSUIPC_USER_LIB NAMES FSUIPC_User FSUIPC_User64 PATHS ${FSUIPC_SDK_DIR} ${FSUIPC_SDK_DIR}/Lib ${FSUIPC_SDK_DIR}/Library ${FSUIPC_SDK_DIR}/Lib64 NO_DEFAULT_PATH)
    if(FSUIPC_USER_LIB)
      target_link_libraries(fsx_monitor PRIVATE ${FSUIPC_USER_LIB})
      target_compile_definitions(fsx_monitor PRIVATE FSUIPC_CLIENT_ENABLED=1)
    else()
      message(WARNING "FSUIPC user library not found in FSUIPC_SDK_DIR; FSUIPC will be disabled.")
    endif()
  else()
    message(WARNING "FSUIPC_SDK_DIR not set. FSUIPC will be disabled.")
  endif()
endif()

if(MSVC)
  target_compile_options(fsx_monitor PRIVATE /W4 /permissive-)
else()
  target_compile_options(fsx_monitor PRIVATE -Wall -Wextra -Wpedantic)
endif()

