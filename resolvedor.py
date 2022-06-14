import time
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
import numpy as np
import random

STATE_01 = "STATE_01"
STATE_02 = "STATE_02"
STATE_10 = "STATE_10"
STATE_11 = "STATE_11"
STATE_100 = "STATE_100"

class localVariables():
    x_atual = random.randint(-1000,1000)
    x = []
    y = []
    roots = []
    order = 0

class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()
    
class step_1_InformBehav(State):
    async def run(self):
        print("step_1_InformBehav running")
        msg = Message(to="luana_gerador@jix.im")     # Instantiate the message
        msg.set_metadata("performative", "request")  # Set the "inform" FIPA performative
        msg.body = "Qual a funcao?"                    # Set the message content
        
        print("Message sent!")
        await self.send(msg)
        self.set_next_state(STATE_02)
    
class step_2_RecieveType(State):
    async def run(self):
        print("step_2_RecieveType running")
        func_order = await self.receive(timeout=10)

        if func_order:
            print("Recieved: ", func_order.body)
            if func_order.body == "1grau":
                variables.order = 1
            elif func_order.body == "2grau":
                variables.order = 2
            elif func_order.body == "3grau":
                variables.order = 3
            else:
                print("Trying to solve function of unknown type")
                self.set_next_state(STATE_02)

            self.set_next_state(STATE_10)

class step_10_FunctionNOrderSolver(State):
    async def run(self):
        print("Sending number ", variables.x_atual)

        msg = Message(to="luana_gerador@jix.im")     # Instantiate the message
        msg.set_metadata("performative", "subscribe")   # Set the "inform" FIPA performative 
        msg.body = str(variables.x_atual)
        await self.send(msg)
        print("Message sent!")
        self.set_next_state(STATE_11)

class step_11_VerifyX(State):
    async def run(self):
        res = await self.receive(timeout=10)
        if res:
            print("y: ", int(res.body))
            if int(res.body) == 0:
                self.set_next_state(STATE_100)
            else:
                variables.x.append(variables.x_atual)
                variables.y.append(int(res.body))
                variables.x_atual += random.randint(-10, 50)

                if(len(variables.y)>=(variables.order+1)):
                    z = np.polyfit(variables.x, variables.y, variables.order)
                    i = random.randint(0, variables.order-1)
                    result = int((np.poly1d(z)).r[i])
                    variables.x_atual = result
                    variables.x_atual = result

                self.set_next_state(STATE_10)
                
class step_100_Result(State):
    async def run(self):
        print("FOUND SOLUTION!")
        print("X = ", variables.x_atual)

class FSMAgent(Agent):
    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_01, state=step_1_InformBehav(), initial=True)
        fsm.add_state(name=STATE_02, state=step_2_RecieveType())
        fsm.add_state(name=STATE_10, state=step_10_FunctionNOrderSolver())
        fsm.add_state(name=STATE_11, state=step_11_VerifyX())
        fsm.add_state(name=STATE_100, state=step_100_Result())

        fsm.add_transition(source=STATE_01, dest=STATE_02)
        fsm.add_transition(source=STATE_02, dest=STATE_10)
        fsm.add_transition(source=STATE_10, dest=STATE_11)
        fsm.add_transition(source=STATE_11, dest=STATE_10)
        fsm.add_transition(source=STATE_11, dest=STATE_100)
        self.add_behaviour(fsm)


if __name__ == "__main__":
    variables = localVariables()
    fsmagent = FSMAgent("user1_@jix.im", "password")
    future = fsmagent.start()
    future.result()

    while fsmagent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            fsmagent.stop()
            break
    print("Agent Resolvedor Finalized")
