import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.Login import Login as loginmodule

app = loginmodule.Login()
app.run()