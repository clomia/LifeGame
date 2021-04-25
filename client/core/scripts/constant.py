# [단위=1세대당 field]그리드 연속연산량
FIRST_PROPHECY_COUNT: int = 100  # 첫 연산량
PROPHECY_COUNT: int = 100  # * 너무 큰 용량은 소켓 버퍼에서 오류가 생기므로 첫 연산량과 동일하게 해둔다.
# [단위:초]메인프로세스-연산쓰레드의 연산,데이터 제공 간격
FIRST_OPERATION_SPEED: int = 50  # 첫 연산 이후의 간격
OPERATION_SPEED: int = 100
# CacheManagementPipe가 사용합니다. 현재 연산제공이 (limit=50)회를 넘어서면 SLOW_OPERATION_SPEED만큼 연산간격을 지연시킵니다.
SLOW_OPERATION_SPEED: int = 0  # * 메모리 문제를 발견되기 전까지는 사용하지 않는다. 초당 1회의 공급을 유지한다.
# 연산프로세스의 prophecy 클래스가 스스로 저장하는 메모리, simul프로세스가 연산을 제공받아서 저장하는 메모리가 과부화되는것을 예방합니다.
# -------------------------------
SIGNAL = object()
PROPHECY_REQUEST = "prophecy".encode("utf-8")
BPRIN_BOOTING_REQUEST = "bprin,booting".encode("utf-8")
PROPHECY_COMPLETE_SIGNAL = "prophecy,complete".encode("utf-8")
# -------------------------------
# todo 여기서 포트번호 검사 & 설정하기
SIMUL_PROC_PORT: int = 12000
SIMUL_PROC_PORT_2: int = 12001
SIMUL_PROC_PORT_3: int = 12002
BPRIN_PROC_PORT: int = 12003
BPRIN_PROC_PORT_2: int = 12004
