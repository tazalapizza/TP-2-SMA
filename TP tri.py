from random import randint, random, seed
seed(1)
from numpy.random import permutation, seed
seed(1)
import tkinter as tk

# environnement de la simulation
class Environnement():
  def __init__(self, N, M, nA, nB, nAg):
    self.gridObj = [[0 for _ in range(M)] for _ in range(N)] # Grille contenant les objets ( 0, "A", "B")
    self.gridAg = [[0 for _ in range(M)] for _ in range(N)]  # Grille contenant les agents (0 ou idAgent)
    self.posAg = [[] for _ in range(nAg+1)] # Liste contenant pour chaque agent sa position x,y
    self.N = N
    self.M = M

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
    # placement initial des agents
    for idA in range(1, nAg+1):
      x, y = 0, 0
      while self.gridObj[x][y] or self.gridAg[x][y]:
        x, y = randint(0, N-1), randint(0, M-1)
      self.gridAg[x][y] = idA
      self.posAg[idA] = [x, y]

  # informer l'agent qui utilise perception de l'objet sur sa case
  def informer(self, idA):
    x, y = self.posAg[idA]
    return(self.gridObj[x][y])

  # depot d'un objet si possible sur la case de l'agent
  def depot(self, idA, obj):
    x, y = self.posAg[idA]
    if self.gridObj[x][y] == 0:
      self.gridObj[x][y] = obj
      return(True)
    return(False)

  # prise d'un objet par l'agent
  def prise(self, idA):
    x, y = self.posAg[idA]
    self.gridObj[x][y] = 0    

  # déplacer l'agent dans l'espace      
  def move(self, idA, dx, dy):
    N, M = self.N, self.M
    x, y = self.posAg[idA]
    x2, y2 = x+dx, y+dy
    if x2 < 0 or x2 >= N:
      x2 -=dx
    if y2 < 0 or y2 >= M:
      y2 -=dy
    if x2 == x and y2 == y:
      return()

    # déplacement impossible : un agent déjà sur la destination
    if self.gridAg[x2][y2]:
      return()

    # déplacement de l'agent sur la destination
    self.gridAg[x][y] = 0
    self.gridAg[x2][y2] = idA
    self.posAg[idA] = [x2, y2]

  # fonction d'affichage de la grille dans la console
  def show(self):
    for x in range(self.N):
      for y in range(self.M):
        if self.gridAg[x][y]:
          print(self.gridAg[x][y], end=" ")
        elif self.gridObj[x][y]:
          print(self.gridObj[x][y], end=" ")
        else:
          print(" ", end=" ")
      print()
    print()

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

# les robots de tri    
class Agent():
  def __init__(self, idA, env, pas, k1, k2, e):
    self.idA = idA # identifiant de l'agent
    self.env = env # environnement
    self.mem = []  # mémoire
    self.transport =  0 # 0 si ne transporte rien, A ou B selon l'objet transporté
    self.pas = pas # pas de déplacement
    self.k1 = k1 # paramètre pour la prise
    self.k2 = k2 # paramètre pour le dépôt
    self.e = e # taux d'erreur

  # récuperer les informations de l'environnement
  def perception(self):
    objet = self.env.informer(self.idA)
    # erreur de perception
    if objet and random() <= self.e :
      objet = {"A":"B", "B":"A"}[objet]
    # ajout de l'objet en mémoire
    self.mem.append(objet)
    if len(self.mem) > 10:
      self.mem.pop(0)

  def action(self):
    k1, k2 = self.k1, self.k2

   # dépôt d'un objet
    if self.transport:
      f = self.mem.count(self.transport) / len(self.mem)
      proba = (f/(k2+f))**2
      if random() <= proba and self.env.depot(self.idA, self.transport) :
        self.transport = 0
        return()

    # prise d'un objet
    objet = self.mem[-1]
    if objet and not(self.transport):
      f = self.mem.count(objet) / len(self.mem)
      proba = (k1/(k1+f))**2
      if random() <= proba :
        self.transport = objet
        self.env.prise(self.idA)
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
        if objet==0:
            self.canva.create_rectangle(*self.liste_case[case],fill = 'white',outline='white')
            
    def affichage(self):
        for i in range(self.width):
            for j in range(self.height):
                objet = self.gridObj[i][j]
                self.affiche_objet(i, j, objet)

def main():
  # paramètres de l'environnement
  N, M = 50, 50
  nAg = 20
  nA, nB = 200, 200
  # paramètres de l'agent
  pas = 1
  k1, k2 = 0.1, 0.3
  e = 1
  # paramètres de la simulation
  T = 1000000
  t_affichage = T//10


  # création des entités
  env = Environnement(N, M, nA, nB, nAg)
  agents = [Agent(i+1, env, pas, k1, k2, e) for i in range(nAg)]

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
    ordre = permutation(nAg)
    for i in ordre:
      agents[i].perception()
      agents[i].action()

  print("Terminaison")
  for agent in agents:
    if agent.transport:
      env.depot(agent.idA, agent.transport)
  interface.affichage()
  interface.update()
  
  # env.show()
  S2 = env.score()
  print(f"Score début : {S1}, Score fin : {S2}")

main()