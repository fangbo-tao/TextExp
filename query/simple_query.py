from data_table import DataTable
import traceback

if __name__ == "__main__":
    hier_meta_dict = {}
    hier_meta_dict['Location'] = '../data/raw/lochier.hier'
    hier_meta_dict['Topic'] = '../data/raw/topichier.hier'

    data_file = "../data/raw/data_table.csv"
    output_file = "../data/query/new_hier/cells"
    #data_file = "../data/raw/new_data_table_no_ner.csv"
    #output_file = "../data/query/new_hier/reduced_cells"


    dt = DataTable(data_file, hier_meta_dict)

    queries = []

    queries.append({'Location':'Illinois'})
    queries.append({'Location':'Illinois', 'Topic':'Sports'})
    #queries.append({'Location':'New York'})
    queries.append({'Location':'China'})
    queries.append({'Location':'Russia'})
    queries.append({'Location':'Japan'})
    queries.append({'Location':'North Korea'})
    queries.append({'Topic':'Asia Pacific'})
    queries.append({'Topic':'Africa'})
    queries.append({'Topic':'Gay Right'})
    queries.append({'Location':'Syria'})
    #queries.append({'Location':'Syria', 'Topic':'Military'}) => 0 doc
    queries.append({'Location':'United States of America', 'Topic':'Military'})
    queries.append({'Location':'United States of America', 'Topic':'Basketball'})
    queries.append({'Location':'United States of America', 'Topic':'Music'})
    queries.append({'Location':'United States of America', 'Topic':'Politics'})
    queries.append({'Location':'United States of America', 'Topic':'Gun Control'})
    queries.append({'Location':'United States of America', 'Topic':'Health'})
    queries.append({'Location':'United States of America', 'Topic':'Immigration'})
    queries.append({'Location':'China', 'Topic':'Politics'})
    queries.append({'Location':'China', 'Topic':'Environment'})
    #queries.append({'Location':'China', 'Topic':'Military'}) => 0 doc
    queries.append({'Location':'China', 'Topic':'Business'})
    queries.append({'Location':'United Kingdom, with Dependencies and Territories', 'Topic':'Business'})
    #queries.append({'Location':'Great Britain', 'Topic':'Business'})

    with open(output_file + ".txt", "w+") as f:
        for query in queries:
            attrs = ""
            for k, v in query.items():
                attrs += "{0}|{1};".format(k, v)
            try:
                doc_list = dt.slice_and_return_doc_id(query)
                print "Attrs:{0};Doc#:{1}".format(attrs, len(doc_list))

                doc_str = [str(i) for i in doc_list]

                wline = "{0}:{1}\n".format(attrs, ",".join(doc_str))

                f.write(wline)
            except:
                print "{1} failed to gen doc list".format(attrs)

    with open(output_file + "_parents.txt", "w+") as f:
        for query in queries:
            attrs = ""
            for k, v in query.items():
                attrs += "{0}|{1};".format(k, v)
            try:
                doc_lists = dt.slice_and_return_parents(query)
                print "Attrs:{0};Parent#:{1}".format(attrs, len(doc_lists))
                doc_strs = []
                for cell_name, doc_list in doc_lists.items():
                    doc_str = ",".join([str(i) for i in doc_list])
                    doc_strs.append(cell_name + "|" + doc_str)

                wline = "{0}:{1}\n".format(attrs, ";".join(doc_strs))

                f.write(wline)
            except:
                print "{1} failed to gen doc list".format(attrs)

    with open(output_file + "_siblings.txt", "w+") as f:
        for query in queries:
            attrs = ""
            for k, v in query.items():
                attrs += "{0}|{1};".format(k, v)
            try:
                doc_lists = dt.slice_and_return_siblings(query)
                print "Attrs:{0};Siblings#:{1}".format(attrs, len(doc_lists))
                doc_strs = []
                for cell_name, doc_list in doc_lists.items():
                    doc_str = ",".join([str(i) for i in doc_list])
                    doc_strs.append(cell_name + "|" + doc_str)

                wline = "{0}:{1}\n".format(attrs, ";".join(doc_strs))

                f.write(wline)
            except:
                print(traceback.format_exc())
                print "{1} failed to gen doc list".format(attrs)

