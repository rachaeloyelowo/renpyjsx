from pyjsx.transpiler import (transpile, JSXElement, JSXExpression, JSXNamedAttribute, JSXText)

# all classes
class Label:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        self.label_name = props['name']

class Character:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        self.char_name = props['var']
        self.char_val = children[0]

class Say:
    def __init__(self, props, children):
        self.props = props
        self.children = children

        self.char_name = props['character']
        self.dialogue = ""
        for child in children:
            if isinstance(child, str):
                self.dialogue += child

        # will fix later to handle expressions



j_file = open("game.jsx", "r")
code = j_file.read()
converted_code = transpile(code) # converted code is an array of JSXElement objects

print(converted_code)

# this dictionary stores all the important values that need to be stored; ie. Characters and Labels
stored_vals = {
    'labels' : {},
    'characters' : {},
    'variables' : {}
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
        
        # after adding all the children, if this is a Character element, checks for potential errors
        if element_type == Character:
            if len(children) < 1:
                raise Exception("You must assign a value to this Character")
            elif len(children) > 1:
                raise Exception("You cannot have more than one value for the Character")
            
            if not isinstance(children[0], str):
                raise Exception("The value of this Character must be a string")

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

    # text
    elif isinstance(root_node, JSXText):
        return (root_node.value)

    # strings
    elif isinstance(root_node, str): # handles strings
        return root_node.strip(" ' ")
