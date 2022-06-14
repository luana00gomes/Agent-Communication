from mimetypes import init
import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import random

from sympy import Ge

class Gerador(Agent):
    def __init__(self, jid: str, password: str, verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        
    order = 0
    res = 0
    x = random.randint(-1000,1000)
    a=0
    b=0
    c=0
    while a*b*c == 0:
        a = random.randint(-100,100)
        b = random.randint(-100, 100)
        c = random.randint(-100, 100)

    y1 = -1 * (a*x)
    y2 = -1 * (a*x*x) - 1*(b*x)
    y3 = -1 * (a*x*x*x) - 1*(b*x*x) - 1 * (c*x)

    class f_x(CyclicBehaviour):
        async def run(self):
            res = await self.receive(timeout=10)
            if res:
                if Gerador.order == 1:
                    msg = Gerador.funcao_1grau(res)
                elif Gerador.order == 2:
                    msg = Gerador.funcao_2grau(res)
                elif Gerador.order == 3:
                    msg = Gerador.funcao_3grau(res)
                else:
                    raise("Erro: Funcao de ordem indefinida")

                await self.send(msg)

    def funcao_1grau(res):
        print("Recieved X = ", res.body)
        x = float(res.body)
        x = float( Gerador.a*x + Gerador.y1 )
        print("Enviou para " + str(res.sender) + " f(",res.body,")= ",x,"=>",int(x))
        msg = Message(to=str(res.sender)) 
        msg.set_metadata("performative", "inform")  
        msg.body = str(int(x))
        return msg
        

    def funcao_2grau(res):
        print("Recieved X = ", res.body)
        x = float(res.body)
        x = float( Gerador.a*x*x + Gerador.b*x + Gerador.y2 )
        print("Enviou para " + str(res.sender) + " f(",res.body,")= ",x,"=>",int(x))
        msg = Message(to=str(res.sender)) 
        msg.set_metadata("performative", "inform")  
        msg.body = str(int(x))
        return msg
    
    def funcao_3grau(res):
        print("Recieved X = ", res.body)
        x = float(res.body)
        x = float( Gerador.a*x*x*x + Gerador.b*x*x + Gerador.c*x + Gerador.y3)
        print("Enviou para " + str(res.sender) + " f(",res.body,")= ",x,"=>",int(x))
        msg = Message(to=str(res.sender)) 
        msg.set_metadata("performative", "inform")  
        msg.body = str(int(x))
        return msg
   
    class tipo_funcao(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                msg = Message(to=str(msg.sender))
                msg.set_metadata("performative", "inform")
                
                if Gerador.order == 0:  #Caso seja a primeira interação, define a ordem da funcao
                    Gerador.order = random.randint(1, 3) 

                msg.body = str(Gerador.order)+"grau"
                if Gerador.order == 1:                    
                    print("Funcao de 1o grau: ", Gerador.x)
                    print("Funcao: ", Gerador.a, "x + (", Gerador.y1, ")")
                elif Gerador.order == 2:
                    print("Funcao de 2o grau: ", Gerador.x)
                    print("Funcao: ", Gerador.a, "x² + ", Gerador.b, "x + ",Gerador.y2)
                elif Gerador.order == 3: 
                    print("Funcao de 3o grau: ", Gerador.x)
                    print("Funcao: ", Gerador.a, "x³ + ", Gerador.b, "x² + ",Gerador.c, "x + ", Gerador.y3)
                
                await self.send(msg)
                print("Respondeu para" + str(msg.sender) + " com " + msg.body)
                

    async def setup(self):
        t = Template()
        t.set_metadata("performative","subscribe")
        tf = self.f_x()
        self.add_behaviour(tf,t)

        ft = self.tipo_funcao()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(ft, template)



if __name__ == "__main__":
    gerador = Gerador("user2_@jix.im", "password")
    future = gerador.start()
    future.result() # wait for receiver agent to be prepared.

    while gerador.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            gerador.stop()
            break
    print("Agent Gerador finalized")
