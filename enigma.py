from tkinter import messagebox
from misc import Enigma1, check_type
from rotor import Rotor


class Enigma:
    """Enigma machine object emulating all mechanical processes in the real enigma machine"""
    def __init__(self, reflector, rotors):
        """
        :param reflector: Reflector label, reflector object will be created automatically
        :param rotors: Three rotor labels, objects will be created automatically
        """
        self.reflector = reflector
        self.rotors = rotors  # Calling property
        self.__plugboard = []
        self.last_output = '' # To avoid sending the same data from rotor position class

    # Plugboard property

    @property
    def plugboard(self):
        """
        Returns the private plugboard pairs
        :return: Private plugboard pairs
        """
        return self.__plugboard

    @plugboard.setter
    @check_type(list)
    def plugboard(self, pairs):
        """
        Sets up plugboard pairs for the plugboard routing
        :param pairs: List of pairs for the plugboard
        """
        assert(len(pairs) <= 13), "Invalid number of pairs!"

        used = []
        plugboard_pairs = []
        for pair in pairs:
            for letter in pair:
                assert(letter not in used), "A letter can only be wired once!"
                used.append(letter)
            plugboard_pairs.append(pair)

        self.__plugboard = plugboard_pairs

    # Rotor property

    @property
    def rotor_labels(self):
        """Returns rotor type ( label ), for the rotor order window."""
        return_list = [self.reflector.label]
        return_list.extend([rotor.label for rotor in self._rotors])
        return return_list

    @property
    def rotors(self):
        """
        Returns private rotor objects
        :return: Rotor objects
        """
        return self._rotors

    @rotors.setter
    @check_type(list)
    def rotors(self, rotors):
        """
        Takes rotor labels and gets the rotors from historical rotors if possible,
        shows a warning if any rotor is invalid
        :param rotors: Rotors labels for creating the rotor objects
        """
        temp = []
        if all([rotor in Enigma1.rotors for rotor in rotors]):
            for rotor in rotors:
                temp.append(Rotor(*Enigma1.rotors[rotor]))
        else:
            messagebox.showwarning('Invalid rotor', 'Some of rotors are not \n'
                                                    'valid, please try again...')
        self._rotors = temp[:]

    @property
    def positions(self):
        """
        Prints rotor wiring ( the offset is visible ), this can visualise therotors turning
        :return: String showing the rotor wiring
        """
        output = '%s %s %s' % (self.rotors[2].back_board,
                                              self.rotors[1].back_board,
                                              self.rotors[0].back_board)

        if self.last_output != output:  # Wiring only printed if anything changed
            return output

        self.last_output = output

    # Reflector property

    @property
    def reflector(self):
        """
        Returns private reflector object
        :return: Reflector object
        """
        return self._reflector

    @reflector.setter
    @check_type(str)
    def reflector(self, reflector):
        """
        Takes a reflector label and gets the reflector from historical reflectors,
        shows a warning if the rotor label is invalid
        :param reflector: Reflector label for creating a reflector object
        """
        if reflector in Enigma1.rotors:
            self._reflector = Rotor(Enigma1.rotors[reflector])
        else:
            messagebox.showwarning('Invalid reflector', 'Invalid reflector,'
                                                        ' please try '
                                                        'again...')

    # Rings settings property

    @property
    def ring_settings(self):
        """
        Returns private ring settings of all the rotors
        :return: All ring settings
        """
        return [rotor.ring_setting for rotor in self.rotors[::-1]]

    @ring_settings.setter
    @check_type(list)
    def ring_settings(self, offsets):
        """
        Takes three numbers as ring settings and applies them to the rotors
        :param offsets: Sets the ring offset
        """
        for rotor, setting in zip(self.rotors, offsets):
            rotor.ring_setting = setting

    # Letter routing process

    @check_type(str)
    def plugboard_route(self, letter):
        """
        Routes a letter trough the plugboard
        :param letter: Letter to route
        :return: Letter routed trough the plugboard
        """
        neighbour = []
        for pair in self.__plugboard:
            if letter in pair:
                neighbour.extend(pair)
                neighbour.remove(letter)
                return neighbour[0]
        return letter # If no connection found

    def rotate_primary(self, places=1):
        """
        Rotates the first rotor, handles rotor turnovers
        :param places: Number of places to rotate ( negative = backwards )
        """
        rotate_next = False
        index = 0
        for rotor in self._rotors:
            if rotate_next or index == 0:
                rotate_next = rotor.rotate(places)
            index += 1

    @check_type(str)
    def button_press(self, letter):
        """
        Takes a letter and simulates enigma encryption, returns a letter that would
        be shown on the enigma lightbulb board
        :param letter: Input letter
        :return: Output encrypted letter
        """
        self.rotate_primary()
        output = letter

        output = self.plugboard_route(output)

        for rotor in self._rotors:
            output = rotor.forward(output)

        output = self.reflector.forward(output)

        for rotor in reversed(self._rotors):
            output = rotor.backward(output)

        output = self.plugboard_route(output)

        return output
