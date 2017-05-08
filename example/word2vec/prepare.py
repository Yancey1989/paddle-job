import paddle.v2 as paddle
import pickle
import os
N=5
output = os.getenv("OUTPUT","./")
train_data_path = os.path.join(output, "train.txt")
test_data_path = os.path.join(output, "test.txt")
word_dict_path = os.path.join(output, "word_dict.pickle")

def dataset_from_reader(filename, reader):
    with open(filename, "w") as fn:
        for batch_id, batch_data in enumerate(reader()):
            batch_data_str = [str(d) for d in batch_data]
            fn.write(",".join(batch_data_str))
            fn.write("\n")
word_dict = paddle.dataset.imikolov.build_dict()
with open(word_dict_path, "w") as dict_f:
    pickle.dump(word_dict, dict_f)

dataset_from_reader(train_data_path, paddle.dataset.imikolov.train(word_dict, N))
dataset_from_reader(test_data_path, paddle.dataset.imikolov.test(word_dict, N))
