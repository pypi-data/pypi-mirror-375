#ifndef EVENT_RATE_TREE_H
#define EVENT_RATE_TREE_H

#include <map>
#include <optional>

#include "sum_tree.hpp"

class EventRateNodeDataTest;
class EventRateTreeTest;

namespace lotto {
using Index = long int;

/*
 * Class to hold event rate data within a binary sum tree node
 * For leaves, should contain an event ID and its corresponding rate
 * For non-leaves, should only contain a (summed) rate
 */
template <typename EventIDType>
class EventRateNodeData {
 public:
  // Construct as a leaf given an event ID and rate
  EventRateNodeData(const EventIDType &event_id, double rate);

  // Return the node's event ID (should only be called on leaves)
  const EventIDType &get_event_id() const;

  // Return the node's rate
  double get_rate() const;

  // Update a node's rate, if it stores an event ID
  void update_rate(double new_rate);

  // Return a new node with no event ID and summed rates
  EventRateNodeData operator+(const EventRateNodeData &rhs_node) const;

 private:
  // Construct as a non-leaf with no event ID and zero rate
  EventRateNodeData();

  // Event ID, which may not exist
  std::optional<EventIDType> event_id;

  // Event rate or summed rate
  double rate;

  // Friend for testing
  friend class ::EventRateNodeDataTest;
};

/*
 * Class to contain a binary sum tree of event rates, with events as leaves
 */
template <typename EventIDType>
class EventRateTree {
 public:
  // Construct tree given list of event IDs and corresponding initial rates
  EventRateTree(const std::vector<EventIDType> &all_event_ids,
                const std::vector<double> &all_rates);

  // Traverse tree and return the event ID of event at index i
  // for which R(i-1) < u <= R(i), where u is the query value
  // and R(i) is cumulative rate of all events up to and including event i
  const EventIDType &query_tree(double query_value) const;

  // Update the rate of a specific event
  void update_rate(const EventIDType &event_id, double new_rate);

  // Return the total rate of all events stored in tree
  double total_rate() const;

  // Get the rate of a specific event
  double get_rate(const EventIDType &event_id) const;

 private:
  using NodeData = EventRateNodeData<EventIDType>;
  using Node = InvertedBinaryTreeNode<NodeData>;

  // Tree to store events and their rates, and to quickly select events
  InvertedBinarySumTree<NodeData> event_rate_tree;

  // Given an EventID, get the corresponding index into the tree leaves
  const std::map<EventIDType, Index> event_to_leaf_index;

  // Generate the leaf index map for all events in tree
  std::map<EventIDType, Index> event_to_leaf_index_map() const;

  // Convert all events and their rates into leaf node data for initialization
  std::vector<NodeData> events_as_leaves(
      const std::vector<EventIDType> &init_events,
      const std::vector<double> &init_rates) const;

  // Based on the rate of the children nodes, pick the left or right
  // child, and subtract the rate out
  const Node *bifurcate(const Node *current_node_ptr,
                        double &running_rate) const;

  // Access leaf data, for testing
  std::vector<NodeData> leaf_data() const;
  std::vector<EventIDType> leaf_ids() const;
  std::vector<double> leaf_rates() const;

  // Friend for testing
  friend class ::EventRateTreeTest;
};

}  // namespace lotto
#endif
