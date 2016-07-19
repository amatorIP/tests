import paramiko
import subprocess, sys
import time
import select

#Declaring services ports and protocol types
services = [#['50001', 'u'],
            #['50001', 'u'],
            ['50010', 'u'],
            ['50011', 'u'],
            ['50012', 'u'],
            ['13400', ''], #empty second parameter mean tcp protocol type
            ['445', ''],
            ['53', 'u'],
            ['53', '']]

send_data = ["*^*open\n",
        "*^*close\n",
        "*^*back\n",
        "*^*forward\n",
        "*^*left\n",
        "*^*right\n",
        "*^*wrong\n",
        "*^*R2D2\n",
        "*^*42\n"]

#open ssh connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy()
)
ssh.connect('198.18.34.1',
            username='root',
            password='root')
nc = ""


#parameters
target_ip = "198.18.34.1"
udp_param = "-u"
listen_param = "-l"
nc_ = "nc"
nc_obd = "nc.netcat-openbsd "
test_status = True

def processing(shell, nc):
    # send from laptop to target
    for d in range(len(send_data)):
        # shell.send(send_data[d])
        nc.stdin.write(send_data[d])
        time.sleep(0.3)
        reply = shell.recv(2024)
        #print "ssh read: " + reply
        str = send_data[d]
        str = str[:-1]
        if str not in reply:
            print "TEST FAILED"
            sys.exit()

    # send from target to laptop
    for d in range(len(send_data)):
        shell.send(send_data[d])
        # nc.stdin.write(send_data[d])
        time.sleep(0.3)
        # reply = shell.recv(2024)
        reply = nc.stdout.readline()
        #print "nc read: " + reply
        str = send_data[d]
        str = str[:-1]
        if str not in reply:
            print "TEST FAILED"
            sys.exit()


#test all ports
for i in range(len(services)):
    print "Port: " + services[i][0] + " : " + services[i][1]
    #exec ssh command & subprocess
    if not services[i][1]:
        print "Debug: " + nc_ + listen_param + services[i][0]
        shell = ssh.invoke_shell()
        print shell.recv(2024)
        cmd = nc_ + " " + listen_param + " "+ services[i][0] + '\n'
        print "cmd: " + cmd
        shell.send(cmd)
        print "nc " + shell.recv(2024)

        time.sleep(1)

        print "Debug subproc: " + nc_ + " " + target_ip + " " + services[i][0]
        nc = subprocess.Popen([nc_, target_ip, services[i][0]],
                              stdout=subprocess.PIPE,
                              stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        time.sleep(0.1)
        processing(shell, nc)
        nc.kill()
        shell.close()

    else:
        print "Debug ssh: " + nc_obd + udp_param + listen_param + services[i][0]
        shell = ssh.invoke_shell()
        cmd = nc_ + ' -v ' + udp_param + " " + listen_param + " " +  services[i][0] +"\n"
        shell.send(cmd)
        shell.recv(2024)

        time.sleep(1)

        print "Debug subproc: " + nc_ + udp_param + target_ip + services[i][0]
        cmd = [nc_, udp_param, target_ip, services[i][0]]

        nc = subprocess.Popen([nc_, udp_param, target_ip, services[i][0]],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        time.sleep(0.1)
        processing(shell, nc)
        nc.kill()
        shell.close()

print "TEST PASSED"
sys.exit()