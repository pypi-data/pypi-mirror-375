#ifndef EVENT_SELECTOR_H
#define EVENT_SELECTOR_H

#include <cassert>
#include <cmath>
#include <memory>
#include <utility>

#include "random.hpp"

namespace lotto {
/*
 * Base class template for event selector
 */
template <typename EventIDType, typename RateCalculatorType,
          typename EngineType>
class EventSelectorBase {
 public:
  typedef typename EngineType::result_type UIntType;

  EventSelectorBase() = delete;

  // Selects a single event, returns the event ID and the time step
  virtual std::pair<EventIDType, double> select_event() = 0;

 protected:
  // Pointer to rate calculator
  const std::shared_ptr<RateCalculatorType> rate_calculator_ptr;

  // Random number generator
  std::shared_ptr<RandomGeneratorT<EngineType> > random_generator;

  // Constructor for use in derived classes
  EventSelectorBase(
      const std::shared_ptr<RateCalculatorType> &rate_calculator_ptr,
      std::shared_ptr<RandomGeneratorT<EngineType> > random_generator =
          std::make_shared<RandomGeneratorT<EngineType> >())
      : rate_calculator_ptr(rate_calculator_ptr),
        random_generator(random_generator) {
    if (this->random_generator == nullptr) {
      this->random_generator =
          std::make_shared<RandomGeneratorT<EngineType> >();
    }
  }

  // Returns the rate given an event ID
  double calculate_rate(const EventIDType &event_id) const {
    double rate = rate_calculator_ptr->calculate_rate(event_id);
    assert(rate >= 0.0);  // rates must be non-negative
    return rate;
  }

  // Returns a list of rates given a list of event IDs
  std::vector<double> calculate_rates(
      const std::vector<EventIDType> &event_ids) const {
    std::vector<double> rates;
    rates.reserve(event_ids.size());
    for (const EventIDType &event_id : event_ids) {
      rates.push_back(calculate_rate(event_id));
    }
    return rates;
  }

  // Returns the time step for Poisson process, given the total rate
  double calculate_time_step(double total_rate) {
    assert(total_rate > 0.0);  // should be positive, avoid divide-by-zero
    double time_step =
        -std::log(random_generator->sample_unit_interval()) / total_rate;
    return time_step;
  }

  // Reseeds the generator
  void reseed_generator(UIntType new_seed) {
    random_generator->reseed_generator(new_seed);
  }
};
}  // namespace lotto
#endif
