def custom_rounded_string(number):
    if number is None:
        return "n.a."
    else:
        return str(round(number, 2)).ljust(4, "0")


def custom_rounded_string_percent(number):
    if number is None:
        return "(n/a)"
    else:
        return "(" + str(round(100*number, 2)) + "%)"


def custom_rounded_string_3(number):
    if number is None:
        return " n/a "
    else:
        return str(round(number, 3)).ljust(5, "0")

def fleiss(interlabeller_data):
    """
    Calculate Fleiss' Kappa for interlabeller agreement.
    cf. https://en.wikipedia.org/wiki/Fleiss%27_kappa#Worked_example

    Args:
        interlabeller_data: Dictionary of interlabeller data:

                            {'document_1':{'labeller_1':'label_x', 'labeller_2':'label_x', ...},
                             'document_2':{'labeller_1':'label_x', 'labeller_2':'label_y', ...},
                             ...
                            }
    Returns:
        Fleiss' Kappa
    """
    # 

    # get all labels from interlabeller data
    labels = set()
    for article_index, assessments in enumerate(interlabeller_data.values()):
        for labeller, label in assessments.items():
            labels.add(label)

    # create label-index-map
    labels = {label:index for index,label in enumerate(labels)}

    # create assessment matrix
    matrix = [[0] * len(labels) for _ in range(len(interlabeller_data))]

    # populate assessment matrix
    for article_index, assessments in enumerate(interlabeller_data.values()):
        for labeller, label in assessments.items():
            matrix[article_index][labels[label]] += 1

    # calculate Fleiss' Kappa
    Pi = []
    for row in matrix:
        Pi.append((1/(sum(row)*(sum(row)-1))) *
                  (sum([value**2 for value in row])-sum(row)))
    pi = []
    for i in range(len(matrix[0])):
        pi.append(sum([row[i] for row in matrix]) /
                  (len(matrix) * sum(matrix[0])))
    Pmean = sum(Pi)/len(Pi)
    Pexp = sum([p**2 for p in pi])
    kappa = (Pmean - Pexp)/(1 - Pexp)
    return kappa

