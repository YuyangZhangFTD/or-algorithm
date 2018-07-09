from Variable import Variable


class Constraint(object):

    def __init__(self, variable):

        if not isinstance(variable, Variable):
            print("Wrong constraint")
            return None
        else:
            self.coefficient_list = variable.next
            self.coefficient_list.insert(0, (
                variable.name, variable.index, variable.coef
            ))
            self.sign = variable.comp_sign
            self.value = variable.comp_value


if __name__ == "__main__":
    a = Variable("a", (0, 1))
    b = Variable("b", (0, 2))
    c = Variable("c", (0, 3))
    constr = Constraint(a * 2 + b * 3 + c * 5 <= 3)
    print(constr.coefficient_list)
    print(constr.sign)
    print(constr.value)
