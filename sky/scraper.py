from utils import *
from training import *
from findLeaf import *

def uniqifyOverTraining(list_of_lists):
    uniques = []    
    for x in list_of_lists[0]: 
        if all([bool(x in y) for y in list_of_lists]):
            uniques.append(x)
        return uniques        

def findParentIdentifiers(x, soup, nLevel=3):
    parents = [] 
    try:
        for parent_attrs in [parent.attrs for parent in x.parents][:nLevel]:
            if len(soup.findAll(**{"attrs" : parent_attrs})) == 1:
                parents.append({"attrs" : parent_attrs})
        for parent_attrs in [{"name" : parent.name} for parent in x.parents][:nLevel]:
            if len(soup.findAll(**{"name" : parent.name})) == 1:
                parents.append({"name" : parent.name})
    except:
        pass
    return parents
    
def findSharedKeyValues(training, trainingLeafs):    
    case_options = [] 
    for soup, case in zip(training.soups, trainingLeafs): 
        options = [] 
        for leaf in case: 
            options.extend(findParentIdentifiers(leaf, soup)) 
            options.extend(findByTag(leaf, soup)) 
        case_options.append(options) 
    shared_options = [] 
    for option in case_options[0]: 
        if all([bool(option in case) for case in case_options]): 
            shared_options.append(option)
    return shared_options        
                        
def findByTag(node, soup, nLevel=5): 
    goodTags = []
    tags = []
    tags.extend([x.name for x in node.parents][:nLevel])
    try:
        tags.append(node.name)
    except:
        pass    
    for tag in tags: 
        if len(soup.findAll(tag)) == 1:
            goodTags.append({"name" : tag}) 
    return goodTags        

def secondLevelDown(soup, outcome, unique_keys): 
    solution = []
    num = 0
    for unique_key in unique_keys:
        num += 1 
        #attempt = soup
        #for key in unique_key: ik denk dat ik hier bedoedle dat ik ook halve matches kan doen
        attempt = soup.find(**unique_key)
        if attempt.text == outcome:
            solution.append([unique_key, BeautifulSoup.get_text])
            
        if stripReasonableWhite(attempt.text) == stripReasonableWhite(outcome):
            solution.append([unique_key, BeautifulSoup.get_text, stripReasonableWhite])

        splitting = splitN(attempt.text, outcome)    
        if splitting:
            for splitable in splitting:    
                solution.append([unique_key, BeautifulSoup.get_text, splitSolution(splitable)]) 
    return solution

def stripReasonableWhite(x):
    return re.sub(r"\s+", " ", x).strip()
    
def splitN(txt, outcome):
    # consider splitting to get result
    txt = stripReasonableWhite(txt)
    outcome = stripReasonableWhite(outcome)
    splitables = set(txt.replace(outcome, '', 1)) - set(' ') 
    options = set()
    for s in splitables:
        for i, x in enumerate(txt.split(s)):
            if stripReasonableWhite(x) == stripReasonableWhite(outcome):
                options.add((s, i))
    return options            

def splitSolution(how):
    def solution(txt):
        return txt.split(how[0])[how[1]]
    return solution    
    
def asNumeric(x): 
    return re.sub("[^0-9]", "", x)


def applySolutionChain(solution, x): 
    for sol in solution: 
        if isinstance(sol, dict):
            x = x.find(**sol)
        else:    
            x = sol(x)
    return x    

def buildSolution(training):
    res = findLeaf(training)
    print("len(res)", len(res))
    x = findSharedKeyValues(training, res)
    print("len(shared)", len(x))
    solutions = secondLevelDown(training.soups[0], training.targets[0], x)
    print("len(solutions)", len(solutions))
    return solutions

def testAutoScraperSolutions(autoScraper, training, verbose = False):
    num = 0
    any_succes = False
    for solution in autoScraper: 
        num += 1
        if all([applySolutionChain(solution, soup) == target for soup, target in zip(training.soups, training.targets)]):
            result = "SUCCESFULL" 
            any_succes = True
        else: 
            result = "UNSUCCESFULL"
        if verbose:    
            print("Scraper method: ", num, " was ", result)
    return any_succes    

def tryUniqueID(c, sp):
    return len(sp.findAll(c.name, attrs=c.attrs)) == 1

def buildNewSolution(tr):
    childs = []
    num = 0
    options = []
    for soup, target in zip(tr.soups, tr.targets):
        print('num',num)
        num+=1
        for c in soup.findChildren():
            try:
                if c.name not in ['body', 'html']:
                    if target in c.text:
                        childs.append([c,  len(c.text)])
            except:
                pass        

        tmp = []            
        for i,x in enumerate(childs[::-1]): 
            if tryUniqueID(x[0], soup):
                attrs = x[0].attrs
                attrs['name'] = x[0].name
                attrs = {'attrs' : attrs}
                if x[0].text == target:
                    tmp.append((attrs, BeautifulSoup.get_text))
                elif stripReasonableWhite(x[0].text) == stripReasonableWhite(target):     
                    tmp.append((attrs, BeautifulSoup.get_text, stripReasonableWhite))
                elif splitN(x[0].text, target):    
                    for splitable in splitN(x[0].text, target):
                        tmp.append((attrs, BeautifulSoup.get_text, splitSolution(splitable)))
                else: 
                    print(len([y for y in x[0].children]))
            else:
                print('not unique', len([y for y in x[0].children])) 
        options.append(tmp)
    good_options = [] 
    if options: 
        for x in options[0]:
            if all(x in y for y in options[1:]): 
                good_options.append(x)
    return good_options    
    
#testAutoScraperSolutions(buildSolution(tr), tr, False)

    

# tr1 = Training("marktplaats-testcase1", "/Users/pascal/GDrive/sky_package/sky/tests/").load()

# tr2 = Training("nieuwsdumper-testcase1", "/Users/pascal/GDrive/sky_package/sky/tests/").load()

# tr3 = Training("nieuwsdumper-testcase2", "/Users/pascal/GDrive/sky_package/sky/tests/").load()

# tr4 = Training("bouwmaterieel-testcase1", "/Users/pascal/GDrive/sky_package/sky/tests/").load()

# tr5 = Training('betterdoctor-doctor-referalls', '/Users/pascal/GDrive/sky_package/sky/tests/').load()

# tr6 = Training("pypi-author", "/Users/pascal/GDrive/sky_package/sky/tests/").load()



