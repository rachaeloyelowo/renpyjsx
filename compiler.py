import sys
from pyjsx.transpiler import (transpile, JSXElement, JSXExpression, JSXNamedAttribute, JSXText)

# all classes *remember that classes are blueprints for objects*

# label class; each label has properties, children inside the label, and a name
class Label:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        if len(props) != 1 or 'name' not in props:
            raise Exception("Label needs a name property")
        
        self.label_name = props['name']



# character class; each character has properties one of which is the variable representation of the characters name and
# children that represents the character's name/variable value (only one child is allowed) 
class Character:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        if len(children) != 1:
            raise Exception("Charcter can only be assigned to one value")

        self.char_name = props['var']
        self.char_val = children[0]


# say class; each piece of dialogue has a character's name/variable name and the dialogue; the name is in the properties under 
# 'character' key so there should only be one key-value pair for the say class; the actual dialogue is in the children (children can be 
# the dialogue or a variable name)

# if the value passed in as the 'character''s value, should have no quotes --> thats why all characters need to be evalutated before anything else
class Say:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        # check if there is a character prop, if not raises an error
        if 'character' not in props:
            raise Exception("Say element needs a 'character' prop to work")

        character = props['character']

        self.char_name = character['value']
        self.is_var = character['isVariable']


        self.dialogue = self.build_dialogue(children)


    def build_dialogue(self, children_arr) -> str:
        dialogue = ""

        for child in children_arr:
            dialogue += child

        return dialogue


# can be changed after definition
class Default:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        self.default_name = props['var']
        self.default_val = children[0]

   
# meant to be static - should not be changed
class Define:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        self.define_name = props['var']
        self.define_val = children[0]

    

# children = array, props = dictionary
class Menu:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        if len(props) > 0:
            raise Exception("Menu should not have any props.")

        if not any(isinstance(child, Option) for child in children):
            raise Exception("Menu needs at least one Option")

        # technically should have no props, all children



# remember that text in the menu is optional but it needs at least one option

class Option: 
    def __init__(self, props, children):
        self.props = props
        self.children = children

        if len(props) != 1 or 'text' not in props:
            raise Exception("Option needs a text property")
        self.option_text = props['text']


class Jump:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        if len(props) != 1 or ('label' not in props and 'expression' not in props):
            raise Exception("Jump needs either a label property or expression property")
        if len(children) != 0:
            raise Exception("Jump shouldn't have any children.")

        if 'label' in props:
            self.destination = props['label']
            self.jump_type = "label"
        elif 'expression' in props:
            self.destination = props['expression']
            self.jump_type = "expression"



class Return:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        if len(props) != 0:
            raise Exception("Return shouldn't have any properties.")
        if len(children) != 0:
            raise Exception("Return shouldn't have any children.")


# actual call
if len(sys.argv) != 2:
    raise Exception("Need to add filename and only filename")
f = sys.argv[1]
if not f.endswith(".rpyjsx"):
    raise Exception("File needs to end with .rpyjsx suffix")

file_name = f.removesuffix(".rpyjsx")

j_file = open(f, "r")
code = j_file.read()
converted_code = transpile(code) # converted code is an array of JSXElement objects


# this dictionary stores all the important values that need to be stored; ie. Characters, Labels, Defines, and Defaults
stored_vals = {
    'labels' : {},
    'characters' : {},
    'defines' : {},
    'defaults' : {}
}

# we want to evaluate each JSX object with evaluate function; for now i will convert them into dictionaries with three key values: {type, props, children}, type is a class, props is a dict, and children is an array
# evaluating a JSXElement -> dictionary of {type, props, children}
# evaluating a JSXAttribute -> tuple of all the key-value pairs
# evaluating a JSXText -> string of value

def evaluate(root_node, stored_vals): 

    # elements
    if isinstance(root_node, JSXElement):
        element_types = {
            'Label' : Label,
            'Character' : Character,
            'Say' : Say,
            'Default' : Default,
            'Define' : Define,
            'Menu' : Menu,
            'Option' : Option,
            'Jump' : Jump,
            'Return' : Return
        }

        # key value pairs of the types of elements that need to be stored and which dictionary they need to be stored in
        must_store = {
            Label : {
                'stored_location' : 'labels',
                'name_location' : 'name' # is in props so props['name'] would give the name of the label ie start
            },
            Character : {
                'stored_location' : 'characters',
                'name_location' : 'var' # is in props so props['var'] would give the name of the character ie 'e'
            },
            Default : {
                'stored_location' : 'defaults',
                'name_location' : 'var'
            },
            Define : {
                'stored_location' : 'defines',
                'name_location' : 'var'
            }
        }

        element_type = root_node.name
        props = {}
        children = []

        # deals with type
        if root_node.name in element_types: 
            element_type = element_types[root_node.name]
        else: 
            raise Exception(f"This element type ({root_node.name}) is not valid.") # handles elements that aren't valid


        # deals with attributes
        for attribute in root_node.attributes:
            a = evaluate(attribute, stored_vals)                
            props[a[0]] = a[1]

        # deals with children
        for child in root_node.children:
            children.append(evaluate(child, stored_vals))
        
        # after adding all the children, if this is a Character/Defualt/Define element, checks for potential errors
        if element_type == Character or element_type == Define or element_type == Default:

            # handles general problem
            if len(children) < 1:
                raise Exception(f"You must assign a value to this {root_node.name} variable.")
            elif len(children) > 1:
                raise Exception(f"You cannot have more than one value type for this {root_node.name} variable.")
            
            # handles type specific problems
            if element_type == Character and not isinstance(children[0], str):
                raise Exception("The value of this Character must be a string")
            
            if (element_type == Define or element_type == Default):
                if not isinstance(children[0], (str, int, float)): # only strings, floats, and integers 
                    raise Exception(f"The value of this {root_node.name} should be a string , float, or integer.")
                

        element_obj = element_type(props, children)

        # checks if the element type needs to stored; if so, stores in stored_vals dictionary
        if element_type in must_store:
            # go into the must_store dictionary, get the the stored location to know where in the stored_vals dictionary to put the object
            # then get the name_location and do props[name_location] to put that into the stored_vals dictionary as a key and the object as its value

            locations = must_store[element_type] # dictionary of locations
            s_l = locations['stored_location'] # stored location of this element
            key_name = locations['name_location'] # where to find the name of the key for the stored_vals to represent this element
            if key_name not in props:
                raise Exception(f"This element, {root_node.name}, does not have a {key_name} prop")

            stored_vals[s_l][props[key_name]] = element_obj

         

        # returns an object corresponding to the right class
        return element_obj
        
    # attributes -> <tag ATTRIBUTE> </tag>
    elif isinstance(root_node, JSXNamedAttribute):
        # computes one attribute as a tuple of 2 items, the name of the attribute and the value of the attribute

        # root_node.name => the name of the attribute variable
        # root_node.value => the value associated with the attribute variable

        if root_node.name == "character":
            # if there is a character attribute and its value is an expression, will combine all parts of JSXExpression and return the
            # attribute name ("character") and a dictionary that stores the value and whether its a variable that is then used later when
            # outputting the text

            # ELSE will store the value but note that its not a variable

            if isinstance(root_node.value, JSXExpression): 
                value = "".join(root_node.value.children)

                return (root_node.name, {
                        "value" : value, 
                        "isVariable" : True
                        })

            else : 
                value = evaluate(root_node.value, stored_vals)

                return (root_node.name, {
                        "value" : value, 
                        "isVariable" : False
                        })

        # or returns a tuple of the attribute name and its actual value
        return (root_node.name, evaluate(root_node.value, stored_vals))

    # expressions
    elif isinstance(root_node, JSXExpression):
        if len(root_node.children) < 1 :
            raise Exception(f"This expression needs a value.") # error if no val in expression  
        
        value = "".join(root_node.children) # takes all the children in the root node and joines them together bc pyjsx computes each char separated by a space as a child [no separator str]
        
        return '[' + value + "]"

    # text
    elif isinstance(root_node, JSXText):
        return (root_node.value)

    # strings
    elif isinstance(root_node, str): # handles strings
        if len(root_node) > 1:
            if (root_node[0] == root_node[-1]) and (root_node[0] in ('"', "'")):
                return root_node[1:-1]


        if root_node.startswith('"') and root_node.endswith('"'):
            return root_node[1:-1]
        return root_node

# checks if a string can be an int * MIGHT DO ONE FOR FLOAT*
def isInteger(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


for node in converted_code:
    evaluate(node, stored_vals)


def generate(node, indent): # takes in the root node and outputs the renpy text in a renpy file
    # go through each node, maybe recursively
    out = ""

    # character name is either a variable : no quotes, or a literal string : quotes
    # each say should have an prop -> "character" : {value : value, isVar : True or False}
    if isinstance(node, Say): # each case should give the text its outputting

        space = " " * indent
        
        if node.is_var:
            out += f'{space}{node.char_name} "{node.dialogue}"'
        else:
            out += f'{space}"{node.char_name}" "{node.dialogue}"'

        return out

    if isinstance(node, Label):

        out += f"label {node.label_name}:\n"

        for child in node.children:
            out += f"{generate(child, indent + 4).rstrip("\n")}\n"

        return out

    if isinstance(node, Menu):
        space = " " * indent

        out += f'{space}menu:\n'
        c_indent = indent + 4
        c_space = " " * c_indent

        for child in node.children:
            if isinstance(child, str):
                out += f'{c_space}"{child}"\n\n'

            elif isinstance(child, Option):
                out += f'{generate(child, c_indent).rstrip("\n")}\n\n'

        return out.rstrip("\n")
    
    if isinstance(node, Option):
        space = " " * indent

        out += f'{space}"{node.option_text}":\n'
        c_indent = indent + 4

        for child in node.children:
            out += f'{generate(child, c_indent).rstrip("\n")}\n'

        return out

    if isinstance(node, Character):
        out += f'define {node.char_name} = Character("{node.char_val}")'
        return out

    if isinstance(node, Default):
        out += f'default {node.default_name} = {node.default_val}'
        return out

    if isinstance(node, Define):
        out += f'define {node.define_name} = {node.define_val}'
        return out

    if isinstance(node, Jump):
        space = " " * indent
        if node.jump_type == "label":
            out += f'{space}jump {node.destination}'
        elif node.jump_type == 'expression':
            out += f'{space}jump expression {node.destination}'

        return out

        

    if isinstance(node, Return):
        space = " " * indent
        out += f'{space}return'

        return out

output = ""

# creates the file and puts all the generated code in it
for val_dict in ["characters", "defines", "defaults", "labels"]:
    for val in stored_vals[val_dict].values():
        output += generate(val, 0) + "\n"
    output += "\n"

output = output.rstrip() + "\n"
file = file_name + ".rpy"
with open(file, "w") as rpy_file:
    rpy_file.write(output)
