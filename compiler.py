from pyjsx.transpiler import (transpile, JSXElement, JSXExpression, JSXNamedAttribute, JSXText)

# all classes *remember that classes are blueprints for objects*

# label class; each label has properties, children inside the label, and a name
class Label:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        self.label_name = props['name']



# character class; each character has properties one of which is the variable representation of the characters name and
# children that represents the character's name/variable value (only one child is allowed) 
class Character:
    def __init__(self, props, children):
        self.props = props
        self.children = children

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

        if character in stored_vals['characters']:
            self.char_name = character
        else:
            self.char_name = '"' + character + '"'


        self.dialogue = self.build_dialogue(children)

    def build_dialogue(self, children_arr) -> str:
        dialogue = ""

        for child in children_arr:
            dialogue += child

        return dialogue


# can be changed after definition
class Default:
    def __init__(self):
        pass

# meant to be static - should not be changed
class Define:
    def __init__(self):
        pass
    


j_file = open("test.rpyjsx", "r")
code = j_file.read()
converted_code = transpile(code) # converted code is an array of JSXElement objects

print(converted_code)

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
            'Define' : Define
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
                'stored_location' : 'defines',
                'name_location' : 'var'
            },
            Define : {
                'stored_location' : 'defaults',
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

    # attributes
    elif isinstance(root_node, JSXNamedAttribute):
        # computes one attribute as a tuple of 2 items, the name of the attribute and the value of the attribute
        return (root_node.name, evaluate(root_node.value, stored_vals))

    # expressions
    elif isinstance(root_node, JSXExpression):
        if len(root_node.children) < 1 :
            raise Exception(f"This expression needs a value.") # error if no val in expression  
     
        value += "".join(root_node.children)
        
        return '[' + value + "]"

    # text
    elif isinstance(root_node, JSXText):
        return (root_node.value)

    # strings
    elif isinstance(root_node, str): # handles strings
        return root_node.strip(" ' ")

# checks if a string can be an int * MIGHT DO ONE FOR FLOAT*
def isInteger(string):
    try:
        int(string)
        return True
    except ValueError:
        return False