
## The main function of this code is to figure out if a value 
## is present in a file or not;
## Simplest trick in the book
## divide and conquer!

def find_target(file, target):
    if len(file) == 0:
        return False
    else:
        n = len(file)//2
        if sorted(file) != file:
            file.sort()
        if file[n] == target:
            return True
        elif file[n] > target:
            return find_target(file[:n], target)
        else:
            return find_target(file[n+1:], target)
