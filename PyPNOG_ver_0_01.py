# -*- coding: utf-8 -*-

import owlready2
from abc import ABC, abstractmethod

#import numpy as np
import pandas as pd

from collections import deque

EPS = 'empty'

#=============================================================================

class PNOGDL_parser:
    
    @staticmethod
    def parse_input_arc_formula(formula):
        
        individual_list = list()
        instance_of_list = list()
        data_properties_dict = dict()
        
        formula = formula.replace('\n', '')
        
        if '{' in formula and '}' in formula:
            
            formula = formula.replace('{', '').replace('}', '')
                  
            subformulas = formula.split('AND')
            
                    
            subformulas = [subformula.rstrip(' ') for subformula in subformulas]
            subformulas = [subformula.lstrip(' ') for subformula in subformulas]
            
            for subformula in subformulas:
                
                if 'INSTANCE-OF' in subformula:
                    
                    subformula_elements = subformula.split('INSTANCE-OF')
                    class_name = subformula_elements[1].rstrip(' ').lstrip(' ')
                    instance_of_list.append(class_name)
                    
                elif 'DP:has' in subformula:
                    
                    subformula_elements = formula.split('DP:')
                    property_pair = subformula_elements[1].replace('DP:', '').rstrip(' ').lstrip(' ').split('=')
                    property_name = property_pair[0].rstrip(' ').lstrip(' ')
                    property_value = property_pair[1].rstrip(' ').lstrip(' ')
                    data_properties_dict[property_name] = property_value
                    
                else:
                    
                    individual_name = subformula.rstrip(' ').lstrip(' ')
                    individual_list.append(individual_name)
                
        else:
            
            class_name = formula.rstrip(' ').lstrip(' ')
            instance_of_list.append(class_name)
            
        return (individual_list, instance_of_list, data_properties_dict)
    
    @staticmethod
    def parse_output_arc_formula(formula):
        
        individual_list = list()
        place_list = list()
        
        if formula.startswith('?self'):
            
            place_name = formula.replace('?self.', '')
            place_name = place_name.rstrip(' ').lstrip(' ')
            
            place_list.append(place_name)
            
        else:
            
            individual_name = formula.rstrip(' ').lstrip(' ')
            individual_list.append(individual_name)
        
        return (individual_list, place_list)
    
#=============================================================================

class SPARQL_generator:
    
    @staticmethod
    def generate_query_for_classes(base_iri, individual_name):
        
        query = """PREFIX IRI: <"""+ base_iri +"""> SELECT ?c WHERE {"""
        
        query = query + """IRI:""" + individual_name + """ a ?c . ?c rdf:type owl:Class}"""
    
        return query
    
    @staticmethod
    def generate_query_for_superclasses(base_iri, class_name):
        
        query = """PREFIX IRI: <""" + base_iri + """> SELECT ?sc WHERE {"""
        
        query = query + """IRI:""" + class_name +""" rdfs:subClassOf* ?sc}"""
    
        return query
    
    @staticmethod
    def generate_query_for_individuals(base_iri, data_properties_dict):
        
        query = """PREFIX IRI: <"""+ base_iri +"""> SELECT ?i WHERE {"""
        
        first_condition = True
        
        for k, v in data_properties_dict.items():
            
            if not first_condition:
                
                query = query + """ AND """
        
            query = query + """?i IRI:""" + k + """=""" + v
            
            first_condition = False
            
        query = query + """}"""
        
        return query
    
#=============================================================================

class MIMPNOG_data_structure(ABC):
     
    def __init__(self, item_list, structure_type, length):
        
        self.data_structure = deque(item_list, maxlen=length)
        self.structure_type = structure_type
        
    def get_length(self):
        
        return len(self.data_structure)
    
    def is_empty(self):
        
        return len(self.data_structure) == 0
    
    def is_full(self):
        
        return len(self.data_structure) == self.data_structure.maxlen
        
    def push(self, element):
        
        self.data_structure.append(element)
            
    
    def pop(self):
        
        if self.structure_type  == 'queue':
            
            return self.data_structure.popleft()
            
        if self.structure_type  == 'stack':
            
            return self.data_structure.pop()
        
    def remove(self, element):
        
        self.data_structure.remove(element)
        
    def check(self):
        
        if self.structure_type == 'list':
            
            return list(self.data_structure)
        
        if self.structure_type  == 'queue':
            
            temp_list = list()
            temp_list.append(self.data_structure[0])
            
            return temp_list
            
        if self.structure_type  == 'stack':
            
            temp_list = list()
            temp_list.append(self.data_structure[-1])
            
            return temp_list
        
    def print(self):
        
        print('   ', list(self.data_structure))
        
    def to_string(self):
        
        return str(list(self.data_structure))
    
    def save_to_dot_file(self, dot_file):
        
        dot_file.write('<<table><tr>')
        
        for i in range(self.data_structure.maxlen):
            
            if i < len(self.data_structure):
                
                dot_file.write('<td border="1">'+self.data_structure[i]+'</td>')
            
            else:
        
                dot_file.write('<td border="1">&epsilon;</td>')
        
        dot_file.write('</tr></table>>')
    
#=============================================================================


class PNOG_element(ABC):

    def __init__(self, ind, name):
        
        self._ind = ind
        self._name = name
        
    @abstractmethod
    def save_to_dot_file(self, dot_file, *arg):
         pass

    @property
    def ind(self):
        return self._ind
    
    @property
    def name(self):
        return self._name
    
class PNOG_place(PNOG_element):

    def __init__(self, ind, name):

        PNOG_element.__init__(self, ind, name)

    def save_to_dot_file(self, dot_file, places, m):

        place_marking = m[self._ind]

        dot_file.write(self.name+' [xlabel="'+self.name+'" label=')
        place_marking.save_to_dot_file(dot_file)
        dot_file.write(' shape=ellipse]\n')


class PNOG_transition(PNOG_element):

    def __init__(self, ind, name):

        PNOG_element.__init__(self, ind, name)
        
        self.input_place_marking_for_firing = dict()

    def save_to_dot_file(self, dot_file, places, transitions, input_arcs, output_arcs):

        dot_file.write(self.name+' [label="'+self._name+'" shape=square]\n')

        for place in places:

            input_arc_description = input_arcs.iloc[place.ind, self._ind]
            
            if str(input_arc_description) == 'nan':
                continue

            dot_file.write(place.name+'->'+self._name +
                           ' [label="'+input_arc_description+'"]\n')

        for place in places:

            output_arc_description = output_arcs.iloc[place.ind, self._ind]

            if str(output_arc_description) == 'nan':
                continue

            dot_file.write(self._name+'->'+place.name +
                           ' [label="'+output_arc_description+'"]\n')

    def is_enabled_for_input_places(self, places, transitions, ontological_graphs, ont_worlds, input_arcs, m):

        enabled = True  
        not_connected = True

        for place in places:

            place_marking = m[place.ind]
            
            input_arc_description = input_arcs.iloc[place.ind, self._ind]
            
            if str(input_arc_description) == 'nan':
                continue
            
            not_connected = False

            if place_marking == None:
                
                return False
            
            if place_marking.is_empty():
                
                return False
            
            individual_list, instance_of_list, data_properties_dict = PNOGDL_parser.parse_input_arc_formula(input_arc_description)
            
            checked_place_marking = place_marking.check()
            
            if len(checked_place_marking) == 1:
            
                place_marking_direct_classes_query = SPARQL_generator.generate_query_for_classes(ontological_graphs[place.ind].base_iri, checked_place_marking[0])
                place_marking_direct_classes = ont_worlds[place.ind].sparql(place_marking_direct_classes_query)
                place_marking_direct_classes = sum(
                    list(place_marking_direct_classes), [])
                
                all_place_marking_class_set = set()

                for cl in place_marking_direct_classes:
                    
                    cl = str(cl).split('.')[1]
                    
                    all_place_marking_classes_query = SPARQL_generator.generate_query_for_superclasses(ontological_graphs[place.ind].base_iri, cl)
                    all_place_marking_classes = ont_worlds[place.ind].sparql(all_place_marking_classes_query)
                    all_place_marking_classes = sum(
                        list(all_place_marking_classes), [])
                    all_place_marking_class_set.update(all_place_marking_classes)
                    
                all_place_marking_class_set = list(
                    map(lambda x: str(x).split('.')[1], all_place_marking_class_set))

                if not set(instance_of_list).issubset(all_place_marking_class_set):
                    
                    enabled = False
                    break
                
                else:
                    
                    self.input_place_marking_for_firing[place.ind] = checked_place_marking[0]
                    
            if len(checked_place_marking) > 1:
                
                place_marking_direct_classes = list()
                
                for pm in checked_place_marking:
                    
                    pm_direct_classes_query = SPARQL_generator.generate_query_for_classes(ontological_graphs[place.ind].base_iri, pm)
                    pm_direct_classes = ont_worlds[place.ind].sparql(pm_direct_classes_query)
                    pm_direct_classes = sum(
                        list(pm_direct_classes), [])
                    
                    place_marking_direct_classes = place_marking_direct_classes + pm_direct_classes
                    
                    all_place_marking_class_set = set()

                    for cl in place_marking_direct_classes:
                        
                        cl = str(cl).split('.')[1]
                        
                        all_place_marking_classes_query = SPARQL_generator.generate_query_for_superclasses(ontological_graphs[place.ind].base_iri, cl)
                        all_place_marking_classes = ont_worlds[place.ind].sparql(all_place_marking_classes_query)
                        all_place_marking_classes = sum(
                            list(all_place_marking_classes), [])
                        all_place_marking_class_set.update(all_place_marking_classes)
                        
                    all_place_marking_class_set = list(
                        map(lambda x: str(x).split('.')[1], all_place_marking_class_set))

                    if not set(instance_of_list).issubset(all_place_marking_class_set):
                        
                        enabled = False
                        break
                    
                    else:
                        
                        self.input_place_marking_for_firing[place.ind] = checked_place_marking[0]
                     
                if enabled == False:
                    break
            
        if not_connected == True:
            
            return False
        
        else:
            
            return enabled

    def is_enabled_for_output_places(self, places, transitions, output_arcs, m):

        enabled = True

        for place in places:

            place_marking = m[place.ind]

            output_arc_description = output_arcs.iloc[place.ind, self._ind]

            if str(output_arc_description) == 'nan':
                continue

            if place_marking.is_full():
                return False

        return enabled

    def is_enabled(self, places, transitions, ontological_graphs, ont_worlds, input_arcs, output_arcs, m):

        return (self.is_enabled_for_input_places(places, transitions, ontological_graphs, ont_worlds, input_arcs, m) and self.is_enabled_for_output_places(places, transitions, output_arcs, m))

    def fire(self, places, transitions, input_arcs, output_arcs, m):

        for place in places:

            output_arc_description = output_arcs.iloc[place.ind, self._ind]
            
            if str(output_arc_description) == 'nan':
            
                continue
            
            else:
                
                individual_list, place_list = PNOGDL_parser.parse_output_arc_formula(output_arc_description)
                
                if len(individual_list) > 0:
                    
                    m[place.ind].push(individual_list[0])
                    break
                    
                if len(place_list) > 0:
                    
                    for input_place in places:
                            
                        if input_place.name == place_list[0]:
                            
                            m[place.ind].push(self.input_place_marking_for_firing[input_place.ind])
                            
                            break
                    
        for place in places:

            input_arc_description = input_arcs.iloc[place.ind, self._ind]

            if str(input_arc_description) == 'nan':
                
                continue
            
            else:   
                
                if m[place.ind].structure_type == 'list':
                    
                    m[place.ind].remove(self.input_place_marking_for_firing[place.ind])
                
                else:
                    
                    m[place.ind].pop()
        
        self.input_place_marking_for_firing = dict()
        
        return m


class PNOG(ABC):
    
    @abstractmethod
    def save_to_dot_file(self, file_name):
        
        pass
    
class IMPNOG(PNOG):
    
    def __init__(self, places, transitions, ontological_graphs, input_arcs, output_arcs, m0):

        self.places = places
        self.transitions = transitions
        self.ontological_graphs = ontological_graphs
        self.input_arcs = input_arcs
        self.output_arcs = output_arcs
        self.m0 = m0

    def save_to_dot_file(self, file_name):

        with open(file_name, "w") as dot_file:

            dot_file.write('digraph PNOG {rankdir="LR";\n')

            for p in self.places:
                p.save_to_dot_file(dot_file, self.places, self.m0)

            for t in self.transitions:
                t.save_to_dot_file(
                    dot_file, self.places, self.transitions, self.input_arcs, self.output_arcs)

            dot_file.write("}")

        dot_file.close()


class MIMPNOG(IMPNOG):

    def __init__(self, places, transitions, data_structures, ontological_graphs, input_arcs, output_arcs, m0):

        super().__init__(places, transitions, ontological_graphs, input_arcs, output_arcs, m0)
        
        self.data_structures = data_structures


#=============================================================================

no_of_steps = 6

ont_world_1 = owlready2.World()

og1 = ont_world_1.get_ontology(
    './EDUTHERIONT_test.owl').load()

places = []
transitions = []
ontological_graphs = [og1]*10
ont_worlds = [ont_world_1]*10

pl1 = PNOG_place(0, 'Input_queue')
places.append(pl1)
pl2 = PNOG_place(1, 'Adult_resp_queue')
places.append(pl2)
pl3 = PNOG_place(2, 'Child_resp_queue')
places.append(pl3)
pl4 = PNOG_place(3, 'AR_glasses_stack')
places.append(pl4)
pl5 = PNOG_place(4, 'Deaf_adult_examination_with_AR_glasses')
places.append(pl5)
pl6 = PNOG_place(5, 'Deaf_adult_examination_without_AR_glasses')
places.append(pl6)
pl7 = PNOG_place(6, 'Deaf_child_examination_with_AR_glasses')
places.append(pl7)
pl8 = PNOG_place(7, 'Deaf_child_examination_without_AR_glasses')
places.append(pl8)
pl9 = PNOG_place(8, 'Experimental_trial_tools_for_adults')
places.append(pl9)
pl10 = PNOG_place(9, 'Experimental_trial_tools_for_children')
places.append(pl10)

tr1 = PNOG_transition(0, 'tr1')
transitions.append(tr1)
tr2 = PNOG_transition(1, 'tr2')
transitions.append(tr2)
tr3 = PNOG_transition(2, 'tr3')
transitions.append(tr3)
tr4 = PNOG_transition(3, 'tr4')
transitions.append(tr4)
tr5 = PNOG_transition(4, 'tr5')
transitions.append(tr5)
tr6 = PNOG_transition(5, 'tr6')
transitions.append(tr6)

input_arcs = pd.read_csv(filepath_or_buffer='Input_arcs.csv', sep=',', header=None)
output_arcs = pd.read_csv(filepath_or_buffer='Output_arcs.csv', sep=',', header=None)

q1 = MIMPNOG_data_structure([], 'queue', 5)
q2 = MIMPNOG_data_structure([], 'queue', 3)
q3 = MIMPNOG_data_structure([], 'queue', 3)
q4 = MIMPNOG_data_structure([], 'stack', 2)
q5 = MIMPNOG_data_structure([], 'queue', 2)
q6 = MIMPNOG_data_structure([], 'queue', 2)
q7 = MIMPNOG_data_structure([], 'queue', 2)
q8 = MIMPNOG_data_structure([], 'queue', 2)
q9 = MIMPNOG_data_structure([], 'list', 2)
q10 = MIMPNOG_data_structure([], 'list', 2)

data_structures = [q1, q2, q3, q4, q5, q6, q7, q8, q8]

q1.push('r1')
q1.push('r2')
q1.push('r3')

q4.push('arg1')
q4.push('arg2')

q9.push('mTalent_Program_Visual_Perception')
q9.push('Visual_perception_exercise_set')

q10.push('mTalent_Program_Visual_Perception')
q10.push('Visual_perception_exercise_set')

m0 = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]

net = MIMPNOG(places, transitions, data_structures, ontological_graphs, input_arcs, output_arcs, m0)

net.save_to_dot_file('pnog_0.dot')

m = m0

for mi in m:
    mi.print()
    
for step in range(no_of_steps):
    
    print('==================== Step: '+str(step+1)+' ====================')

    for transition in transitions:
        
        enabled = transition.is_enabled(places, transitions, ontological_graphs, ont_worlds, input_arcs, output_arcs, m)
                
        if enabled == True:
    
            print('   Enabled transition: '+transitions[transition.ind].name)
            print('   Fired')
            m = transition.fire(places, transitions, input_arcs, output_arcs, m)
    
            for mi in m:
                mi.print()
                
            net.save_to_dot_file('pnog_'+str(step+1)+'_'+transition.name+'.dot')
            
            break

#=============================================================================
