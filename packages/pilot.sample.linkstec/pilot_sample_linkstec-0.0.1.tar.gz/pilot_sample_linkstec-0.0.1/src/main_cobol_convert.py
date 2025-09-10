
import time

import controller

if __name__ == '__main__':
    start = time.time()
    CobolController = controller.Controller()
    CobolController.run("cobol_single.properties")
    end = time.time()
    print(f"処理時間: {end - start:.2f}秒")

