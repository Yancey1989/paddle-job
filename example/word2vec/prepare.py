import paddle.v2 as paddle
import pickle
N=5
word_dict = paddle.dataset.imikolov.build_dict()
with open("word_dict.pickle", "w") as dict_f:
    pickle.dump(word_dict, dict_f)

def dataset_from_reader(filename, reader):
    with open(filename, "w") as f:
        for batch_id, batch_data in enumerate(reader()):
            batch_data_str = [str(d) for d in batch_data]
            fn.write(",".join(batch_data_str))
            fn.write("\n")

dataset_from_reader("train.txt", paddle.dataset.imikolov.train(word_dict, N))
dataset_from_reader("test.txt", paddle.dataset.imikolov.test(word_dict, N))
