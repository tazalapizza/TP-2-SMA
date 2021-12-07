from random import randint, random, seed
seed(1)
from numpy.random import permutation, seed
seed(1)
import tkinter as tk
from time import sleep

# environnement de la simulation
class Environnement():
  def __init__(self, N, M, nA, nB, nC, nAg, r, ds):
    self.gridObj = [[0 for _ in range(M)] for _ in range(N)] # Grille contenant les objets ( 0, "A", "B", "CX")
    self.gridAg = [[[] for _ in range(M)] for _ in range(N)] # Grille contenant les agents (0 ou une liste [idAgent])
    self.gridSon = [[0 for _ in range(M)] for _ in range(N)] # Grille contenant le son présent sur une case
    self.posAg = [[] for _ in range(nAg+1)] # Liste contenant pour chaque agent sa position x,y
    self.agents = []
    self.N = N
    self.M = M
    self.evap = r # attenuation temporelle du son
    self.attenuation = ds # attenuation spatiale du son
    self.couples = [] # liste des couples d'agents qui coopèrent pour porter un objet C

    # placement initial des objets
    for _ in range(nA):
      x, y = 0, 0
      while self.gridObj[x][y]:
        x, y = randint(0, N-1), randint(0, M-1)
      self.gridObj[x][y] = "A"
    for _ in range(nB):
      x, y = 0, 0
      while self.gridObj[x][y]:
        x, y = randint(0, N-1), randint(0, M-1)
      self.gridObj[x][y] = "B"
    for _ in range(nC):
      x, y = 0, 0
      while self.gridObj[x][y]:
        x, y = randint(0, N-1), randint(0, M-1)
      self.gridObj[x][y] = "C0"
    # placement initial des agents
    for idA in range(1, nAg+1):
      x, y = 0, 0
      while self.gridObj[x][y] or self.gridAg[x][y]:
        x, y = randint(0, N-1), randint(0, M-1)
      self.gridAg[x][y] = [idA]
      self.posAg[idA] = [x, y]

  # informer l'agent qui utilise perception de l'objet sur sa case et du son autour de lui
  def informer(self, idA):
    N, M = self.N, self.M
    x, y = self.posAg[idA]
    son = [[0 for _ in range(3)] for _ in range(3)]
    for dx in range(-1, 2):
      for dy in range(-1, 2):
        x2, y2 = x+dx, y+dy
        if x2 >= 0 and x2 < self.N and y2 >= 0 and y2 < self.M:
          son[dx+1][dy+1] = self.gridSon[x2][y2]
    return(self.gridObj[x][y], son)

  # depot d'un objet si possible sur la case de l'agent
  def depot(self, idA, obj):
    # print(f"{idA} dépot {obj}")
    x, y = self.posAg[idA]
    # l'agent lache la prise de l'objet C qu'il tenait seul
    if obj in ["C1", "C4"]:
      self.gridObj[x][y] = "C0"
      return(True)    
    # dépôt impossible
    if self.gridObj[x][y] != 0:
      return(False)
    # un des deux agents qui transportaient le C le lache
    elif obj in ["C2", "C3"]:
      self.gridObj[x][y] = "C4"
      for couple in self.couples:
        if idA in couple:
          self.couples.remove(couple)
          break
    # dépôt d'un objet A ou B
    else:
      self.gridObj[x][y] = obj
    return(True)

  # prise d'un objet par l'agent
  def prise(self, idA):
    x, y = self.posAg[idA]
    # print(f"{idA} prise {self.gridObj[x][y]}")
    # prise d'un objet C seul
    if self.gridObj[x][y] == "C0":
      self.gridObj[x][y] = "C1"
    # prise d'un objet C déjà tenu par un agent
    elif self.gridObj[x][y] == "C1":
      self.gridObj[x][y] = "C2"
      self.couples.append(self.gridAg[x][y][:])
    # détection par le premier agent qu'un deuxième est venu l'aider
    elif self.gridObj[x][y] == "C2":
      self.gridObj[x][y] = 0
    # prise d'un objet A ou B
    else:
      self.gridObj[x][y] = 0    

  # déplacer l'agent dans l'espace      
  def move(self, idA, dx, dy):
    x, y = self.posAg[idA]
    x2, y2 = x+dx, y+dy
    if x2 < 0 or x2 >= self.N:
      x2 -=dx
    if y2 < 0 or y2 >= self.M:
      y2 -=dy
    if x2 == x and y2 == y:
      return()
       
    # déplacement impossible : un agent déjà sur la destination qui ne demande pas d'aide
    if self.gridAg[x2][y2] and not(len(self.gridAg[x2][y2]) == 1 and self.gridObj[x2][y2] == "C1"):
      return()
    
    # l'agent bouge avant que son partenaire soit informé du couple
    if self.gridObj[x][y] == "C2":
      return()
    
    # déplacement du couple
    for couple in self.couples:
      if idA in couple:
        # cas particulier ignoré ci-dessus
        if len(self.gridAg[x2][y2]) == 1 and self.gridObj[x2][y2] == "C1":
          return()
        for agent in couple:
          self.gridAg[x][y].remove(agent)
          self.gridAg[x2][y2].append(agent)
          self.posAg[agent] = [x2, y2]
          # mise à jour de la mémoire du partenaire pour la continuité
          if agent != idA :
            self.agents[agent].perception()
        return()
  
    # déplacement de l'agent sur la destination
    self.gridAg[x][y].remove(idA)
    self.gridAg[x2][y2].append(idA)
    self.posAg[idA] = [x2, y2]

  # émission du son par l'agent
  def emission(self, idA, volume):
    x, y = self.posAg[idA]
    ds = self.attenuation
    for dx in range(-ds, ds+1):
      for dy in range(-ds, ds+1):
        x2, y2 = x+dx, y+dy
        if x2 >= 0 and x2 < self.N and y2 >= 0 and y2 < self.M:
          self.gridSon[x2][y2] += max(0, volume * (1 - (dx**2+dy**2)**0.5/ds))

  # attenuation du son après un tour
  def evaporation(self):
    for x in range(self.N):
      for y in range(self.M):
        self.gridSon[x][y] = self.evap*self.gridSon[x][y]
        if self.gridSon[x][y] < 1:
          self.gridSon[x][y] = 0

  # fonction d'affichage de la grille dans la console
  def show(self):
    for x in range(self.N):
      for y in range(self.M):
        if self.gridAg[x][y]:
          print(",".join(list(map(str, self.gridAg[x][y]))), end=".")
        if self.gridObj[x][y]:
          print(self.gridObj[x][y][0], end="|")
        else:
          print("  |", end="")
      print()
    print()

  # fonction d'affichage du son dans la console
  def showSon(self):
    for x in range(self.N):
      self.gridSon[x] = list(map(int, self.gridSon[x]))
      print("|".join(list(map(str, self.gridSon[x]))))

  # évaluation du score d'une grille selon la position des objets
  def score(self):
    S = 0
    for x in range(self.N):
      for y in range(self.M):
        if self.gridObj[x][y]:
          S -= 1
          for dx in range(-1, 2):
            for dy in range(-1, 2):
              try:
                S += int(self.gridObj[x][y] == self.gridObj[x+dx][y+dy])
              except:
                pass
    return(S)
    
class Agent():
  def __init__(self, idA, env, pas, k1, k2, e, volume, patience):
    self.idA = idA # identifiant de l'agent
    self.env = env # environnement
    self.mem = []  # mémoire
    self.transport =  0 # 0 si ne transporte rien, A ou B selon l'objet transporté
    self.pas = pas # pas de déplacement
    self.k1 = k1 # paramètre pour la prise
    self.k2 = k2 # paramètre pour le dépôt
    self.e = e # taux d'erreur
    self.volume = volume # intensité d'émission du son
    self.son = [] # grille du son alentour perçu
    self.patience = patience # nombre de tours max à attendre de l'aide
    self.waiting = 0 # nombre de tours passés à attendre

  # récuperer les informations de l'environnement
  def perception(self):
    objet, son = self.env.informer(self.idA)
    self.son = son
    # # erreur de perception de l'objet
    # if objet and random() <= self.e :
    #   objet = {"A":"B", "B":"A"}[objet]

    # ne pas remplir la mémoire pendant l'attente
    if self.waiting:
      # il y a un changement de bots, on remplace (changement d'état)
     if objet and self.mem[-1] != objet and objet[0] == "C" :
      self.mem[-1] = objet
      return()

    # le partenaire a laché l'objet
    if objet == "C4" and self.transport:
      self.transport = "C4"
      return()

    # ajout de l'objet en mémoire
    self.mem.append(objet)
    if len(self.mem) > 10:
      self.mem.pop(0)

  # comptage des objets du même type en mémoire
  def countObj(self, objet):
    if objet in ["A", "B"]:
      return(self.mem.count(objet))
    return(len([i for i in self.mem if "C" in str(i)]))

  def action(self):
    k1, k2 = self.k1, self.k2 

    # en attente d'aide
    if self.waiting :
      # un bot est venu aider
      if self.mem[-1] == "C2":
        self.env.prise(self.idA)
        self.transport = "C3"
        self.waiting = 0
      # trop d'attente
      elif self.waiting == self.patience:
        self.waiting = 0
        self.env.depot(self.idA, "C1")
      # toujours seul
      else:
        self.env.emission(self.idA, self.volume)
        self.waiting += 1
      return()

    # lache l'objet C que l'allié a laché
    if self.transport == "C4":
      self.env.depot(self.idA, self.transport)
      self.transport = 0
      return()

    # dépôt d'un objet
    if self.transport:
      f = self.countObj(self.transport) / len(self.mem)
      proba = (f/(k2+f))**2
      # deux porteurs donc on réduit la proba
      if self.transport[0] == "C":
        proba *= 0.5
      if random() <= proba and self.env.depot(self.idA, self.transport) :
        self.transport = 0
        return()

    # prise d'un objet
    objet = self.mem[-1]
    if objet and not(self.transport):
      f = self.countObj(objet) / len(self.mem)
      proba = (k1/(k1+f))**2
      if random() <= proba :
        # un bot sur l'objet C qui attend de l'aide
        if objet == "C1" :
          self.env.prise(self.idA)
          self.transport = "C2"
          return()
        # un objet C seul
        if objet == "C0" :
          self.env.prise(self.idA)
          self.waiting = 1
        # prise d'un objet A ou B
        else:
          self.env.prise(self.idA)
          self.transport = objet
        return()

    # déplacement vers le son
    if self.transport == 0:
      directions = []
      sonMax = 0
      m = self.son[1][1]
      for i in range(3):
        for j in range(3):
          self.son[i][j] -= m
      for dx in range(-1, 2):
        for dy in range(-1, 2):
          if self.son[dx+1][dy+1] > sonMax:
            sonMax = self.son[dx+1][dy+1]
            directions = [[dx, dy]]
          elif sonMax and self.son[dx+1][dy+1] == sonMax:
            directions.append([dx, dy])
      if directions:
        direction = directions[randint(0, len(directions)-1)]
        self.env.move(self.idA, direction[0], direction[1])
        return()

    # déplacement aléatoire
    dx, dy = 0, 0
    while dx == 0 and dy == 0:
      dx, dy = randint(-1, 1)*self.pas, randint(-1, 1)*self.pas
    self.env.move(self.idA, dx, dy)
    return()

# interface Tkinter pour afficher la grille
class Interface(tk.Tk):
    def __init__(self,env):
        tk.Tk.__init__(self)
        self.gridObj = env.gridObj
        self.width = len(self.gridObj)
        self.height = len(self.gridObj[0])
        w = self.width
        h = self.height
        pixel = 15
        self.canva = tk.Canvas(self,width=w*pixel,height=h*pixel,bg='white')
        self.canva.pack()
        for i in range(1,w):
            self.canva.create_line(i*pixel,0,i*pixel,w*pixel)
        for i in range(1,h):
            self.canva.create_line(0,i*pixel,h*pixel,i*pixel)
        self.liste_case = [(i*pixel+2,j*pixel+2,i*pixel+pixel-2,j*pixel+pixel-2) for i in range(w) for j in range(h)]
        
    def affiche_objet(self, ligne, col, objet):
        case = ligne*self.width + col
        if objet=="A":
            self.canva.create_rectangle(*self.liste_case[case],fill = 'red',outline='red')
        if objet=="B":
            self.canva.create_rectangle(*self.liste_case[case],fill = 'blue',outline='blue')
        if objet=="C0" or objet == "C4":
            self.canva.create_rectangle(*self.liste_case[case],fill = 'green',outline='green')
        if objet==0:
            self.canva.create_rectangle(*self.liste_case[case],fill = 'white',outline='white')
            
    def affichage(self):
        for i in range(self.width):
            for j in range(self.height):
                objet = self.gridObj[i][j]
                self.affiche_objet(i, j, objet)

def main():
  # paramètres de l'environnement
  N, M = 20, 20
  nAg = 5
  nA, nB, nC = 20, 20, 20  #0.05 *N*M
  evap = 0.1
  attenuation = N//5
  # paramètres de l'agent
  pas = 1
  k1, k2 = 0.1, 0.3
  e = 0
  volume = N//5
  patience = N//2
  # paramètres de la simulation
  T = 100000
  t_affichage = T//10


  # création des entités
  env = Environnement(N, M, nA, nB, nC, nAg, evap, attenuation)
  agents = [Agent(i+1, env, pas, k1, k2, e, volume, patience) for i in range(nAg)]
  env.agents = [None] + agents

  interface = Interface(env)
  interface.affichage()
  interface.update_idletasks()
  interface.update()

  #env.show()
  S1 = env.score()

  # simulation principale
  for epoch in range(T):
    if epoch%t_affichage == 0:
      print(epoch)
      interface.affichage()
      interface.update()
    ordre = range(nAg)
    for i in ordre:
      agents[i].perception()
      agents[i].action()
    env.evaporation()

  print("Terminaison")
  for agent in agents:
    if agent.transport:
      env.depot(agent.idA, agent.transport)
  interface.affichage()
  interface.update()
  
  # env.show()
  S2 = env.score()
  print(f"Score début : {S1}, Score fin : {S2}")
  sleep(10)

main()