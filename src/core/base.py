from enum import Enum


class Actions(Enum):
    BUFF = 1
    NORMAL_ATTACK = 2
    SPECIAL_ATTACK = 3


class Character:
    def __init__(self, name, hp, power):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.power = power
        self.iron_skin_active = False
        self.arcane_shield_active = False
        self.assassin_charges = 0

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        if self.arcane_shield_active:
            self.arcane_shield_active = False
            return
        if self.iron_skin_active:
            damage = damage // 2
            self.iron_skin_active = False
        self.hp = max(0, self.hp - damage)

    def get_effective_power(self):
        if self.assassin_charges > 0:
            return self.power + 40
        return self.power

    def use_buff(self):
        pass

    def normal_attack(self, target):
        dmg = self.get_effective_power()
        if self.assassin_charges > 0:
            self.assassin_charges -= 1
        target.take_damage(dmg)

    def special_attack(self, target):
        pass


class Warrior(Character):
    def __init__(self):
        super().__init__("Warrior", 260, 40)

    def use_buff(self):
        self.iron_skin_active = True
        self.hp = min(self.max_hp, self.hp + 40)

    def special_attack(self, target):
        target.take_damage(75)


class Mage(Character):
    def __init__(self):
        super().__init__("Mage", 200, 50)

    def use_buff(self):
        self.arcane_shield_active = True

    def special_attack(self, target):
        target.take_damage(90)


class Assassin(Character):
    def __init__(self):
        super().__init__("Assassin", 235, 30)

    def use_buff(self):
        self.assassin_charges = 3

    def special_attack(self, target):
        dmg = self.get_effective_power() * 2
        if self.assassin_charges > 0:
            self.assassin_charges -= 1
        target.take_damage(dmg)


class Battle:
    def __init__(self, char1, char2):
        self.char1 = char1
        self.char2 = char2
        self.is_over = False

    def _execute_action(self, actor, target, action):
        if action == Actions.BUFF:
            actor.use_buff()
        elif action == Actions.NORMAL_ATTACK:
            actor.normal_attack(target)
        elif action == Actions.SPECIAL_ATTACK:
            actor.special_attack(target)

    def _class_name(self, char):
        return type(char).__name__

    def play_turn(self, act_1, act_2):
        if self.is_over:
            return "This battle is over!"

        self._execute_action(self.char1, self.char2, act_1)
        if not self.char2.is_alive():
            self.is_over = True
            return (f"The {self._class_name(self.char1)} won! "
                    f"Remaining HP = {self.char1.hp}")

        self._execute_action(self.char2, self.char1, act_2)
        if not self.char1.is_alive():
            self.is_over = True
            return (f"The {self._class_name(self.char2)} won! "
                    f"Remaining HP = {self.char2.hp}")

        return (f"{self._class_name(self.char1)} HP = {self.char1.hp}, "
                f"{self._class_name(self.char2)} HP = {self.char2.hp}")