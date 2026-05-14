import memory
import os

# test disk controller
def test_disk():
    io = memory.IO()
    disk = io.disk
    image = open("test.img","r+b")
    disk.disks[0] = image
    disk.device.value = 0
    disk.sector0.value = 0
    disk.sector1.value = 0
    disk.sector2.value = 0
    disk.sector3.value = 0

    # test read
    disk.commandPort.write(memory.lbaDisk.Command.read.value)
    data = bytes([disk.data.read() for _ in range(512)])
    image.seek(0)
    assert data == image.read(512), "Disk read failed"

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    test_disk()
    print("Disk controller test passed")
