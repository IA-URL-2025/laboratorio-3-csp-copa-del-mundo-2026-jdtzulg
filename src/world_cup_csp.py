import copy

class WorldCupCSP:
    def __init__(self, teams, groups, debug=False):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        :param teams: Diccionario con los equipos, sus confederaciones y bombos.
        :param groups: Lista con los nombres de los grupos (A-L).
        :param debug: Booleano para activar trazas de depuración.
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

        # Las variables son los equipos.
        self.variables = list(teams.keys())

        # El dominio de cada variable inicialmente son todos los grupos.
        self.domains = {team: list(groups) for team in self.variables}

    def get_team_confederation(self, team):
        return self.teams[team]["conf"]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        """
        Verifica si asignar un equipo a un grupo viola
        las restricciones de confederación o tamaño del grupo.
        """
        teams_in_group = [t for t, g in assignment.items() if g == group]
        
        # implementar restricción de tamaño del grupo (máximo 4)
        if len(teams_in_group) >= 4:
            return False

        # implementar restricción de que no puede haber dos equipos del mismo bombo    
        new_team_pot = self.get_team_pot(team)
        for t in teams_in_group:
            if self.get_team_pot(t) == new_team_pot:
                return False
                
        new_confs = []
        if team == "Playoff Inter-1":
            new_confs = ["AFC", "CAF", "OFC"]
        elif team == "Playoff Inter-2":
            new_confs = ["CONMEBOL", "CONCACAF", "AFC"]
        elif team == "Playoff UEFA-A/B/C/D":
            new_confs = ["UEFA"]
        else:
            new_confs = [self.get_team_confederation(team)]
            
        exceptions = {
            "K": ["Portugal", "Iran", "Uzbekistan", "Playoff Inter-2", "Irán", "Uzbekistán"],
            "D": ["USA", "Colombia", "Paraguay", "Curazao", "Curacao"]
        }
        
        # implementar restricción de confederaciones (máximo 1, excepto UEFA máximo 2)
        current_conf_counts = {
            "UEFA": 0, "CONMEBOL": 0, "CONCACAF": 0, "AFC": 0, "CAF": 0, "OFC": 0
        }
        
        for t in teams_in_group:
            if t == "Playoff Inter-1":
                for c in ["AFC", "CAF", "OFC"]: current_conf_counts[c] += 1
            elif t == "Playoff Inter-2":
                for c in ["CONMEBOL", "CONCACAF", "AFC"]: current_conf_counts[c] += 1
            elif t == "Playoff UEFA-A/B/C/D":
                current_conf_counts["UEFA"] += 1
            else:
                c = self.get_team_confederation(t)
                if c in current_conf_counts:
                    current_conf_counts[c] += 1
                
        is_normal_valid = True
        for c in new_confs:
            limit = 2 if c == "UEFA" else 1
            if current_conf_counts.get(c, 0) + 1 > limit:
                is_normal_valid = False
                break
                
        if is_normal_valid:
            return True
            
        if group in exceptions and team in exceptions[group]:
            if all(t in exceptions[group] for t in teams_in_group):
                return True
                
        return False

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones.
        Debe eliminar valores inconsistentes en dominios futuros.
        Retorna True si la propagación es exitosa, False si algún dominio queda vacío.
        """
        # Hacemos una copia de los dominios actuales para modificarla de forma segura
        new_domains = copy.deepcopy(domains)

        unassigned_vars = [v for v in self.variables if v not in assignment]
        
        # implementar forward checking para filtrar grupos inválidos
        for var in unassigned_vars:
            valid_groups = []
            for group in new_domains[var]:
                if self.is_valid_assignment(group, var, assignment):
                    valid_groups.append(group)
            
            new_domains[var] = valid_groups
            if not valid_groups:
                return False, new_domains

        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Heurística MRV (Minimum Remaining Values).
        Selecciona la variable no asignada con el dominio más pequeño.
        """
        unassigned_vars = [v for v in self.variables if v not in assignment]
        if not unassigned_vars:
            return None

        # implementar heurística MRV (Minimum Remaining Values)    
        return min(unassigned_vars, key=lambda v: len(domains[v]))

    def backtrack(self, assignment, domains=None):
        """
        Backtracking search para resolver el CSP.
        """
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Condición de parada: Si todas las variables están asignadas, retornamos la asignación.
        if len(assignment) == len(self.variables):
            return assignment

        # 1. Seleccionar variable con MRV
        var = self.select_unassigned_variable(assignment, domains)
        if var is None:
            return None

        # 2. Probar cada grupo en el dominio de la variable seleccionada    
        for group in domains[var]:
            if self.is_valid_assignment(group, var, assignment):
                local_assignment = assignment.copy()
                local_assignment[var] = group
                
                # 3. Verificar si es válido, aplicar FC
                success, new_domains = self.forward_check(local_assignment, domains)
                
                if success:
                # 4. Aplicar backtrack
                    result = self.backtrack(local_assignment, new_domains)
                    if result is not None:
                        return result

        return None
