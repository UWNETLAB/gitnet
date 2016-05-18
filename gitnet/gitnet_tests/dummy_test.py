import gitnet as gn

# Example path for testing.
rp_path = "/Users/joelbecker/Documents/Work/Networks Lab/rad_pariphernalia"
my_log = gn.get_log(rp_path,mode="stat")

print(my_log.tags)
print(my_log.attributes())
print(my_log)

print(my_log.csv(fname="my_logs.txt"))
#my_log.browse()