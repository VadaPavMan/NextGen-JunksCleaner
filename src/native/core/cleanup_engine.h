#pragma once

#include "junkscleaner/jc_types.h"
#include <filesystem>
#include <string>
#include <vector>

namespace junkscleaner::cleanup {

struct CleanupTargetDef {
    std::string target_id;
    std::string display_name;
    std::string description;
    jc_risk_level_t risk_level{JC_RISK_LOW};
    std::filesystem::path default_root;
};

std::filesystem::path resolve_target_root(
    const std::string& target_id,
    const char* custom_root_override
);

jc_status_t scan_target(
    const jc_scan_options_t* options,
    std::vector<jc_cleanup_item_t>& out_items,
    uint64_t& out_total_bytes
);

jc_status_t execute_cleanup(
    const jc_cleanup_options_t* options,
    jc_cleanup_report_t* out_report
);

} // namespace junkscleaner::cleanup
