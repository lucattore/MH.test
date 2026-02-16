import tkinter as tk
import random

class JogoDoutorLucas:
    def __init__(self):
        self.doc_nome = ""
        self.doc_hp, self.doc_hp_max = 20, 20
        self.doc_dano_base = 6
        self.doc_pos = [20, 10]
        self.gold = 0
        
        # Sistema de múltiplos inimigos
        self.inimigos_floresta = [] 
        self.ini_nome = "Cachorro Pulguento"
        self.ini_hp, self.ini_hp_max = 15, 15
        self.ini_dano = 6
        self.ini_vivo = True 
        
        self.turno_atual = 1
        self.fase_combate = "ESPERA" 
        self.tipo_ataque = ""
        self.tecla_correta = ""
        self.msg_combate = ""
        self.timer_valor = 0
        self.offset_x, self.offset_y = 0, 0 
        self.esquiva_sucesso = False
        
        self.modo_jogo = "MENU"
        self.mapa_atual = "VILA"
        self.prompt_entrada = ""
        self.dialogo_npc = ""
        self.alvo_transicao = ""
        
        self.quest_ativa = None
        self.progresso_quest = 0
        self.menu_quest_index = 0
        self.opcoes_quest = [
            {"txt": "1. 3 Cachorro Pulguento = 20g", "meta": 3, "alvo": "Cachorro Pulguento", "reward": 20},
            {"txt": "2. 4 Siriricas Nervosas = 50g", "meta": 4, "alvo": "Siririca Nervosas", "reward": 50},
            {"txt": "3. 5 Cangurus Pernetas = 80g", "meta": 5, "alvo": "Canguru Pernetas", "reward": 80}
        ]

        self.npcs_vila = []
        self.contratante_pos = [23, 2]
        self.gerar_npcs()

        self.casas = {
            "CASA_LUCAS": {"porta": [20, 12], "corpo": [[19,13],[20,13],[21,13],[19,14],[20,14],[21,14]], "cor": "#A52A2A"},
            "FERREIRO":   {"porta": [34, 7],  "corpo": [[34,6],[35,6],[36,6],[36,7],[34,8],[35,8],[36,8]], "cor": "#808080"},
            "MERCADOR_ALIMENTOS": {"porta": [6, 10], "corpo": [[4,9],[5,9],[6,9],[4,10],[4,11],[5,11],[6,11]], "cor": "#DEB887"},
            "MERCADOR_GERAL": {"porta": [6, 4], "corpo": [[4,3],[5,3],[6,3],[4,4],[4,5],[5,5],[6,5]], "cor": "#DEB887"}
        }
        self.limites_vila = [[x,y] for x in range(40) for y in range(15) if (x==0 or x==39 or y==14 or (y==0 and not(18<=x<=22)))]

        self.root = tk.Tk()
        self.root.withdraw()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        self.win_main = tk.Toplevel(self.root)
        self.larg_p = int(sw * 0.6)
        self.win_main.geometry(f"{self.larg_p}x{sh-100}+0+0")
        self.win_main.configure(bg="black")
        self.canvas = tk.Canvas(self.win_main, bg="black", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.win_main.bind("<Key>", self.input_teclado)

        self.entry_nome = tk.Entry(self.win_main, font=("Courier", 18), justify="center")

        self.win_status = tk.Toplevel(self.root)
        self.win_status.geometry(f"{int(sw*0.2)}x{int(sh*0.3)}+{self.larg_p+20}+0")
        self.lbl_status = tk.Label(self.win_status, font=("Courier", 12), justify="left", bg="#1a1a1a", fg="white", padx=10, pady=10)
        self.lbl_status.pack(expand=True, fill="both")
        self.win_status.withdraw()

        self.win_combate = tk.Toplevel(self.root)
        self.win_combate.geometry(f"{int(sw*0.25)}x{int(sh*0.6)}+{self.larg_p+20}+{int(sh*0.3)+50}")
        self.lbl_combate = tk.Label(self.win_combate, font=("Courier", 11), justify="center", bg="black", fg="white", padx=10, pady=10, borderwidth=2, relief="ridge")
        self.lbl_combate.pack(expand=True, fill="both")
        self.win_combate.withdraw()

        self.ciclo_vida()
        self.root.mainloop()

    def gerar_npcs(self):
        self.npcs_vila = [{'pos': [random.randint(5, 35), random.randint(5, 12)]} for _ in range(random.randint(3, 5))]

    def gerenciar_inimigos_floresta(self):
        if self.mapa_atual != "FLORESTA" or self.modo_jogo != "EXPLORACAO": return
        
        # Spawn aleatório (máximo 2)
        if len(self.inimigos_floresta) < 2 and random.random() > 0.95:
            rx, ry = random.randint(5, 35), random.randint(2, 12)
            if [rx, ry] != self.doc_pos:
                self.inimigos_floresta.append({'pos': [rx, ry], 'hp': 15})

        # Movimentação aleatória dos cachorros
        for ini in self.inimigos_floresta:
            if random.random() > 0.9:
                nx, ny = ini['pos'][0] + random.choice([-1, 0, 1]), ini['pos'][1] + random.choice([-1, 0, 1])
                if 0 < nx < 39 and 0 < ny < 14:
                    ini['pos'] = [nx, ny]

    def mover_npcs(self):
        if self.modo_jogo != "EXPLORACAO": return
        for npc in self.npcs_vila:
            if random.random() > 0.9:
                nx, ny = npc['pos'][0] + random.choice([-1, 0, 1]), npc['pos'][1] + random.choice([-1, 0, 1])
                if [nx, ny] not in self.limites_vila and not any([nx, ny] in d["corpo"] for d in self.casas.values()) and [nx, ny] != self.contratante_pos:
                    npc['pos'] = [nx, ny]

    def iniciar_combate(self, inimigo_obj):
        self.inimigo_atual_ref = inimigo_obj
        self.ini_hp = inimigo_obj['hp']
        self.ini_vivo = True
        self.modo_jogo = "COMBATE"
        self.win_combate.deiconify()
        self.turno_atual = 1
        self.proximo_turno_combate()

    def proximo_turno_combate(self):
        if not self.ini_vivo or self.modo_jogo != "COMBATE": return
        self.win_main.focus_force()
        self.offset_x, self.offset_y = 0, 0
        self.esquiva_sucesso = False
        ataques = ["ATAQUE PELA DIREITA", "ATAQUE PELA ESQUERDA", "ATAQUE DE FRENTE", "ATAQUE POR TRÁS"]
        self.tipo_ataque = random.choice(ataques)
        regras = {"ATAQUE PELA DIREITA": "A", "ATAQUE PELA ESQUERDA": "D", "ATAQUE DE FRENTE": "S", "ATAQUE POR TRÁS": "W"}
        self.tecla_correta = regras[self.tipo_ataque]
        self.fase_combate = "PREPARO"; self.timer_valor = 1.2; self.msg_combate = ""; self.timer_preparo_combate()

    def timer_preparo_combate(self):
        if self.fase_combate != "PREPARO" or self.modo_jogo != "COMBATE": return
        if self.timer_valor > 0.1:
            self.timer_valor -= 0.1; self.root.after(100, self.timer_preparo_combate)
        else:
            self.fase_combate = "ESQUIVA"; self.timer_valor = 0.9; self.timer_esquiva_combate()

    def timer_esquiva_combate(self):
        if self.fase_combate != "ESQUIVA" or self.modo_jogo != "COMBATE": return
        if self.timer_valor > 0.1:
            self.timer_valor -= 0.1; self.root.after(100, self.timer_esquiva_combate)
        else:
            if self.fase_combate == "ESQUIVA": self.processar_resultado_combate(False)

    def processar_resultado_combate(self, acertou):
        if self.fase_combate != "ESQUIVA": return
        self.fase_combate = "ESPERA"
        if not acertou: 
            self.doc_hp -= self.ini_dano
            self.msg_combate = "DANO RECEBIDO!"
        else:
            self.esquiva_sucesso = True
            self.msg_combate = "DESVIOU!"
            if self.tecla_correta == "D": self.offset_x = 15
            elif self.tecla_correta == "A": self.offset_x = -15
            elif self.tecla_correta == "S": self.offset_y = 3
            elif self.tecla_correta == "W": self.offset_y = -3
        
        if self.doc_hp <= 0: self.root.after(1000, self.derrota_combate)
        elif self.turno_atual >= 3 and self.esquiva_sucesso: self.root.after(1000, self.preparar_contra_ataque)
        else: self.turno_atual += 1; self.root.after(1000, self.proximo_turno_combate)

    def preparar_contra_ataque(self):
        self.fase_combate = "REAÇÃO"; self.timer_valor = 0.90; self.tecla_correta = random.choice(["Q", "E"])
        self.msg_combate = f"CONTRA-ATAQUE: {self.tecla_correta}"; self.timer_reacao_combate()

    def timer_reacao_combate(self):
        if self.fase_combate != "REAÇÃO" or self.modo_jogo != "COMBATE": return
        if self.timer_valor > 0.1: self.timer_valor -= 0.1; self.root.after(100, self.timer_reacao_combate)
        else:
            if self.fase_combate == "REAÇÃO": self.finalizar_ataque_doc(False)

    def finalizar_ataque_doc(self, acertou):
        self.fase_combate = "ESPERA"
        if acertou: 
            self.ini_hp -= self.doc_dano_base
            self.msg_combate = f"GOLPE DIRETO! -{self.doc_dano_base}"
        else: 
            self.msg_combate = "VOCÊ ERROU O GOLPE!"
        
        if self.ini_hp <= 0: 
            self.root.after(1000, self.vitoria_combate)
        else: 
            self.turno_atual += 1; self.root.after(1000, self.proximo_turno_combate)

    def vitoria_combate(self):
        self.ini_vivo = False
        self.ini_hp = 0
        if self.inimigo_atual_ref in self.inimigos_floresta:
            self.inimigos_floresta.remove(self.inimigo_atual_ref)
        self.modo_jogo = "EXPLORACAO"
        if self.quest_ativa and self.quest_ativa["alvo"] == self.ini_nome: 
            self.progresso_quest += 1
        self.win_combate.withdraw()

    def derrota_combate(self):
        self.modo_jogo = "EXPLORACAO"; self.mapa_atual = "VILA"; self.doc_hp = 20; self.doc_pos = [20,10]; self.win_combate.withdraw()

    def renderizar_mapa_canvas(self):
        ex, ey, ox, oy = 15, 20, 50, 50
        for y in range(15):
            for x in range(40):
                char, cor = "", ""
                if [x, y] == self.doc_pos: char, cor = "@", "#00FFFF"
                elif self.mapa_atual == "VILA":
                    if [x,y] == self.contratante_pos: char, cor = "C", "#FF00FF"
                    elif any(npc['pos'] == [x,y] for npc in self.npcs_vila): char, cor = "n", "#CCCCCC"
                    elif [x,y] in self.limites_vila: char, cor = "Y", "#228B22"
                    else:
                        for n, d in self.casas.items():
                            if [x,y] in d["corpo"]: char, cor = "▒", d["cor"]; break
                            if [x,y] == d["porta"]: char, cor = "П", "#FFFFFF"; break
                        if not char and y == 0 and 18 <= x <= 22: char, cor = "=", "#FFFF00"
                elif self.mapa_atual == "FLORESTA":
                    # Renderiza inimigos da lista
                    for ini in self.inimigos_floresta:
                        if [x, y] == ini['pos']: char, cor = "###", "red"
                    if not char:
                        if [x,y] in self.limites_vila: char, cor = "Y", "#228B22"
                        elif y == 0 and 18 <= x <= 22: char, cor = "=", "#FFFF00"
                        elif (x+y) % 7 == 0: char, cor = "'", "#32CD32"
                else: 
                    if (x == 0 or x == 39 or y == 0 or (y == 14 and not(18<=x<=22))): char, cor = "▒", "#555555"
                    elif y == 14 and 18 <= x <= 22: char, cor = "П", "#FFFFFF"
                    elif self.mapa_atual == "CASA_LUCAS":
                        if [x,y] == [5,4]: char, cor = "田", "#8B4513"
                        elif [x,y] == [5,8]: char, cor = "█", "#444444"
                        elif [x,y] == [34,4]: char, cor = "♨", "#FF4500"
                    elif self.mapa_atual == "FERREIRO":
                        if y == 6 and 10 <= x <= 30: char, cor = "═", "#808080"
                        elif [x,y] == [20, 5]: char, cor = "&", "#FFD700"
                        elif [x,y] == [25, 4]: char, cor = "🔥", "#FF0000"
                if char: self.canvas.create_text(ox + x*ex, oy + y*ey, text=char, fill=cor, font=("Courier", 14))
        
        if self.prompt_entrada or self.dialogo_npc:
            self.canvas.create_rectangle(self.larg_p/2-240, 340, self.larg_p/2+240, 440, fill="#222", outline="white", width=2)
            self.canvas.create_text(self.larg_p/2, 380, text=self.prompt_entrada or self.dialogo_npc, fill="yellow", font=("Courier", 11, "bold"), width=440)
            self.canvas.create_text(self.larg_p/2, 425, text="Barra de Espaço: Confirmar | W A S D: Sair", fill="gray", font=("Courier", 8))

    def render_combate_visual(self):
        espacos_x = " " * (15 + self.offset_x); quebras_y = "\n" * (2 + self.offset_y)
        b_doc = f"{quebras_y}{espacos_x}   O   \n{espacos_x} /|\\ \n{espacos_x} / \\ "
        b_ini = "      ###      \n     #####     \n     #   #     "
        aviso = f"ATENÇÃO:\n{self.tipo_ataque}!" if self.fase_combate == "PREPARO" else "!!! APERTE AGORA !!!" if self.fase_combate == "ESQUIVA" else self.msg_combate
        st = f"{self.ini_nome} HP: {self.ini_hp}/{self.ini_hp_max}\n{self.doc_nome} HP: {self.doc_hp}/{self.doc_hp_max}"
        self.lbl_combate.config(text=f"{st}\n\n{b_ini}\n\n{b_doc}\n\n{aviso}\n\nTURNO: {self.turno_atual}")

    def ciclo_vida(self):
        self.canvas.delete("all")
        if self.modo_jogo == "MENU":
            self.canvas.create_text(self.larg_p/2, 200, text="JOGUINHO LEGAL DO LUCAS\n\n[ ENTER ]", fill="#00FF00", font=("Courier", 20))
        elif self.modo_jogo == "NOME":
            self.canvas.create_text(self.larg_p/2, 150, text="NOME DO DOUTOR:", fill="white", font=("Courier", 18))
            self.entry_nome.place(x=self.larg_p/2-100, y=200, width=200); self.entry_nome.focus_set()
        elif self.modo_jogo in ["EXPLORACAO", "QUEST_MENU", "COMBATE"]:
            self.atualizar_status(); self.atualizar_janela_missao()
            if self.mapa_atual == "VILA": self.mover_npcs()
            elif self.mapa_atual == "FLORESTA": self.gerenciar_inimigos_floresta()
            self.renderizar_mapa_canvas()
        if self.modo_jogo == "COMBATE": self.render_combate_visual()
        self.root.after(100, self.ciclo_vida)

    def atualizar_status(self):
        q_info = f"\n\nQUEST: {self.progresso_quest}/{self.quest_ativa['meta']} {self.quest_ativa['alvo']}" if self.quest_ativa else "\n\nSEM QUEST ATIVA"
        st = f" DOUTOR: {self.doc_nome}\n HP: {self.doc_hp}/20\n GOLD: {self.gold}g\n LOCAL: {self.mapa_atual}{q_info}"
        self.lbl_status.config(text=st)

    def atualizar_janela_missao(self):
        if self.modo_jogo == "QUEST_MENU":
            msg = "--- QUADRO DE MISSÕES ---\n\n"
            for i, opt in enumerate(self.opcoes_quest):
                seta = "-> " if i == self.menu_quest_index else "   "
                msg += f"{seta}{opt['txt']}\n"
            self.lbl_combate.config(text=msg + "\n[Espaço] Aceitar | [N] Sair", fg="cyan")

    def input_teclado(self, event):
        key = event.keysym.upper(); c = event.char.upper()
        if self.modo_jogo == "MENU" and key == "RETURN": self.modo_jogo = "NOME"
        elif self.modo_jogo == "NOME" and key == "RETURN":
            if self.entry_nome.get(): self.doc_nome = self.entry_nome.get(); self.entry_nome.destroy(); self.modo_jogo = "EXPLORACAO"; self.win_status.deiconify(); self.win_combate.deiconify()
        elif self.modo_jogo == "QUEST_MENU":
            if c == 'W': self.menu_quest_index = (self.menu_quest_index - 1) % 3
            elif c == 'S': self.menu_quest_index = (self.menu_quest_index + 1) % 3
            elif c == 'N': self.modo_jogo = "EXPLORACAO"
            elif key == "SPACE":
                self.quest_ativa = self.opcoes_quest[self.menu_quest_index]; self.progresso_quest = 0; self.dialogo_npc = "Boa sorte!"; self.modo_jogo = "EXPLORACAO"
                self.root.after(2000, lambda: setattr(self, 'dialogo_npc', ""))
        elif self.modo_jogo == "EXPLORACAO":
            if self.prompt_entrada:
                if key == "SPACE":
                    if self.alvo_transicao == "QUEST": self.modo_jogo = "QUEST_MENU"; self.prompt_entrada = ""
                    elif self.alvo_transicao == "CANCELAR_QUEST": self.quest_ativa = None; self.modo_jogo = "QUEST_MENU"; self.prompt_entrada = ""
                    else:
                        prev = self.mapa_atual; self.mapa_atual = self.alvo_transicao; self.prompt_entrada = ""
                        self.doc_pos = list(self.casas[prev]["porta"]) if prev in self.casas else [20, 12]
                        if self.mapa_atual == "FLORESTA": self.doc_pos = [20, 13]
                    return
                elif c in "WASD": self.prompt_entrada = ""; return
            dx, dy = (0,-1) if c=='W' else (0,1) if c=='S' else (-1,0) if c=='A' else (1,0) if c=='D' else (0,0)
            prox = [self.doc_pos[0]+dx, self.doc_pos[1]+dy]
            
            if self.mapa_atual == "VILA":
                if prox == self.contratante_pos:
                    self.alvo_transicao = "CANCELAR_QUEST" if self.quest_ativa else "QUEST"
                    self.prompt_entrada = "Quer matar um bichinho feio?"; return
                if prox[1] < 0 and 18 <= prox[0] <= 22: self.prompt_entrada = "Ir para FLORESTA?"; self.alvo_transicao = "FLORESTA"; return
                for n, d in self.casas.items():
                    if prox == d["porta"]: self.prompt_entrada = f"Entrar em {n}?"; self.alvo_transicao = n; return
                if prox in self.limites_vila or any(prox in d["corpo"] for d in self.casas.values()): return
            elif self.mapa_atual == "FLORESTA":
                # Checa colisão com cachorros
                for ini in self.inimigos_floresta:
                    if prox == ini['pos']:
                        if random.random() < 0.1:
                            self.inimigos_floresta.remove(ini)
                            self.dialogo_npc = "O cachorro pulguento fugiu de medo!"
                            self.root.after(2000, lambda: setattr(self, 'dialogo_npc', ""))
                        else:
                            self.iniciar_combate(ini)
                        return
                if prox[1] >= 14 and 18 <= prox[0] <= 22: self.prompt_entrada = "Sair para a VILA?"; self.alvo_transicao = "VILA"; return
            else:
                if prox[1] >= 14 and 18 <= prox[0] <= 22: self.prompt_entrada = "Sair para a VILA?"; self.alvo_transicao = "VILA"; return
            
            if dx+dy != 0: self.doc_pos = prox; self.dialogo_npc = ""
        elif self.modo_jogo == "COMBATE":
            if self.fase_combate == "ESQUIVA" and key == self.tecla_correta: self.processar_resultado_combate(True)
            elif self.fase_combate == "REAÇÃO" and key == self.tecla_correta: self.finalizar_ataque_doc(True)

JogoDoutorLucas()