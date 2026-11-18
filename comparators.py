def string_compare(this, that):
    max_index = max(len(this), len(that))
    
    for index in range(max_index):
        this_ch = ord(this[index]) if index < len(this) else 0
        that_ch = ord(that[index]) if index < len(that) else 0
        value = this_ch - that_ch
        if value != 0:
            return value
    
    return 0
