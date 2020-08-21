import numpy as np


from detection_accounting import *

#ZLV275 - actual value

#Notes:
## Append only 6-symbols long data (!)
## Prioritize match_template



LP_Array = ['ZLV275','ZLY275','ZLY27S',
'ZIY275','AIVS7S','ZLV27S','SYV375']

print(GetTrueLPRecord(LP_Array))

"""
print(LP_char_Array)

LP_matrix = np.matrix(LP_char_Array)
LP_matrix_t = LP_matrix.transpose()


print(LP_matrix_t)
"""