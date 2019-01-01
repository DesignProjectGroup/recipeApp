from django.shortcuts import render
from comments.models import ProbabilityOfWords, CommentDataSet
from snowballstemmer import stemmer
import re


def show_comment(request):
    ProbabilityOfWords.objects.all().delete()
    read_file("comments/text_files/positives.txt")
    read_file("comments/text_files/negatives.txt")
    tag_comment_dataset("comments/text_files/test_positives.txt")
    tag_comment_dataset("comments/text_files/test_negatives.txt")
    calculate_accuracy()
    # do_semantic_analysis("Tarif çok zor olsada yapmaya değer")
    # do_semantic_analysis("tarif yapması çok zor")
    return render(request, 'comments/comment_template.html', {})


# train txt leri okur ve kelimeleri olasılıklarını database e kaydeder.
def read_file(file_name):
    stem = stemmer('turkish')
    all_words_list = []
    word_count_pair = {}

    stopwords_file = \
        open("comments/text_files/stopwords.txt", "r").read()
    stopwords_list = stopwords_file.split("\n")

    file = open(file_name, "r").read()
    all_lines_list = file.split("\n")
    for line in all_lines_list:
        words_of_one_sentence = line.split(" ")
        for word in words_of_one_sentence:
            word = re.sub(r'[^\w\s]', '', word)
            word = word.lower()
            word_list = [word]
            word = stem.stemWords(word_list)[0]

            if word in stopwords_list:
                continue
            else:
                all_words_list.append(word)
                if word in word_count_pair.keys():
                    word_count_pair[word] += 1
                else:
                    word_count_pair[word] = 1
    count_of_all_words = len(all_words_list)
    count_of_unique_words = len(word_count_pair.keys())
    if "positives.txt" in file_name:
        for word in word_count_pair.keys():
            word_probability = calculate_probability(word, word_count_pair, count_of_all_words,
                                                     count_of_unique_words)
            try:
                probability_object = ProbabilityOfWords.objects.get(word=word)
            except ProbabilityOfWords.DoesNotExist:
                probability_object = None

            if probability_object is not None:
                probability_object.probabilityOfPositive = word_probability
            else:
                ProbabilityOfWords.objects.update_or_create(word=word, probabilityOfPositive=word_probability)

        for i in ProbabilityOfWords.objects.filter(probabilityOfNegative=0):
            i.probabilityOfNegative = 1 / (count_of_all_words + count_of_unique_words)
            i.save()

    if "negatives.txt" in file_name:
        for word in word_count_pair.keys():
            word_probability = calculate_probability(word, word_count_pair, count_of_all_words, count_of_unique_words)
            try:
                probability_object = ProbabilityOfWords.objects.get(word=word)
            except ProbabilityOfWords.DoesNotExist:
                probability_object = None

            if probability_object is not None:
                probability_object.probabilityOfNegative = word_probability
            else:
                ProbabilityOfWords.objects.update_or_create(word=word, probabilityOfNegative=word_probability)

        for i in ProbabilityOfWords.objects.filter(probabilityOfPositive=0):
            i.probabilityOfPositive = 1 / (count_of_all_words + count_of_unique_words)
            i.save()


def calculate_probability(word, word_count_pair, count_of_all_words, count_of_unique_words):
    count_of_word = word_count_pair[word]
    count_of_word += 1

    probability = count_of_word / (count_of_all_words + count_of_unique_words)
    return probability


# verilen cümlenin pozitif mi negatif mi olduğuna karar verir
def do_semantic_analysis(sentence):
    sentence_probability_of_negative = 1
    sentence_probability_of_positive = 1
    stem = stemmer('turkish')

    stopwords_file = open("comments/text_files/stopwords.txt", "r").read()
    stopwords_list = stopwords_file.split("\n")
    words_list = sentence.split(" ")
    for word in words_list:
        word = re.sub(r'[^\w\s]', '', word)
        word = word.lower()
        x = [word]
        word = stem.stemWords(x)[0]

        if word in stopwords_list:
            continue
        else:
            try:
                word_probability_of_negative = ProbabilityOfWords.objects.get(word=word).probabilityOfNegative
            except ProbabilityOfWords.DoesNotExist:
                word_probability_of_negative = 1
            try:
                word_probability_of_positive = ProbabilityOfWords.objects.get(word=word).probabilityOfPositive
            except ProbabilityOfWords.DoesNotExist:
                word_probability_of_positive = 1

            sentence_probability_of_negative *= word_probability_of_negative
            sentence_probability_of_positive *= word_probability_of_positive
    if sentence_probability_of_positive > sentence_probability_of_negative:
        result = "positive"
    elif sentence_probability_of_positive < sentence_probability_of_negative:
        result = "negative"
    else:
        result = "notr"
    return result


# test comment data seti positive veya negative olarak tagler.
def tag_comment_dataset(test_file_path):
    all_test_lines_list = open(test_file_path, "r").read().split("\n")
    if "test_negatives.txt" in test_file_path:
        for i in all_test_lines_list:
            CommentDataSet.objects.update_or_create(text=i, isPositive="negative")

    if "test_positives.txt" in test_file_path:
        for i in all_test_lines_list:
            CommentDataSet.objects.update_or_create(text=i, isPositive="positive")


# comment test set için doğruluk yüzdesi bulur
def calculate_accuracy():
    right = 0
    wrong = 0
    all_test_objects = CommentDataSet.objects.all()
    for test_sentence in all_test_objects:
        is_positive = do_semantic_analysis(test_sentence.text)
        if is_positive == test_sentence.isPositive:
            # print(test_sentence.text)
            # print(test_sentence.isPositive)
            right += 1
        else:
            wrong += 1
    count_of_all_test_sentences = len(all_test_objects)
    accuracy = right / count_of_all_test_sentences
    print(accuracy)
    return accuracy
