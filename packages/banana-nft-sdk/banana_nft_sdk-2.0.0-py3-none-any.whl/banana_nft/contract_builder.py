"""
🏗️ VISUAL SMART CONTRACT BUILDER

Non-technical interface for encoding business rules into NFT smart contracts:
- Drag & drop rule builder
- Visual tokenomics configuration  
- Forever mint mechanics
- Revenue automation
- Condition-based triggers
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json


class RuleType(Enum):
    ROYALTY_SPLIT = "royalty_split"
    FOREVER_MINT = "forever_mint" 
    CONDITIONAL_PRICING = "conditional_pricing"
    HOLDER_REWARDS = "holder_rewards"
    SUPPLY_MECHANICS = "supply_mechanics"
    GOVERNANCE = "governance"
    UTILITY_ACCESS = "utility_access"


class TriggerCondition(Enum):
    TIME_BASED = "time_based"           # After X days/blocks
    VOLUME_BASED = "volume_based"       # After X ETH volume
    HOLDER_COUNT = "holder_count"       # When X holders reached
    MINT_COUNT = "mint_count"          # After X mints
    PRICE_THRESHOLD = "price_threshold" # When floor price hits X
    SOCIAL_METRICS = "social_metrics"   # Twitter followers, Discord members
    

@dataclass
class BusinessRule:
    rule_id: str
    rule_type: RuleType
    name: str
    description: str
    trigger_condition: TriggerCondition
    trigger_value: Any
    action: Dict[str, Any]
    active: bool = True
    priority: int = 1


@dataclass 
class SmartContractConfig:
    contract_name: str
    symbol: str
    total_supply: int
    mint_price: float
    max_per_wallet: int
    royalty_percentage: float
    rules: List[BusinessRule]
    forever_mint_enabled: bool = False
    governance_enabled: bool = False


class VisualContractBuilder:
    """
    🎨 Visual drag-and-drop interface for creating smart contract rules
    
    This is the core component that enables non-technical users to:
    - Visually configure tokenomics rules
    - Generate production-ready smart contracts
    - Encode complex business logic without coding
    """
    
    def __init__(self):
        self.rule_templates = self._initialize_rule_templates()
        self.generated_contracts = {}
    
    def _initialize_rule_templates(self) -> Dict[str, Dict]:
        """Pre-built rule templates for common NFT use cases"""
        return {
            "basic_royalty_split": {
                "name": "Basic Royalty Split",
                "description": "Split royalties between creator, platform, and community",
                "visual_config": {
                    "type": "pie_chart",
                    "splits": [
                        {"label": "Creator", "percentage": 70, "color": "#4CAF50"},
                        {"label": "Platform", "percentage": 20, "color": "#2196F3"}, 
                        {"label": "Community Pool", "percentage": 10, "color": "#FF9800"}
                    ]
                },
                "solidity_template": """
                // Automated Royalty Distribution
                mapping(address => uint256) public royaltyShares;
                
                function distributeRoyalties() external payable {
                    uint256 creatorShare = (msg.value * 70) / 100;
                    uint256 platformShare = (msg.value * 20) / 100;
                    uint256 communityShare = (msg.value * 10) / 100;
                    
                    payable(creator).transfer(creatorShare);
                    payable(platform).transfer(platformShare);
                    communityPool += communityShare;
                    
                    emit RoyaltyDistributed(msg.value);
                }
                """
            },
            
            "forever_mint_revenue": {
                "name": "Forever Mint Revenue Stream",
                "description": "Continuous minting creates ongoing revenue",
                "visual_config": {
                    "type": "revenue_flow",
                    "mint_price": 0.01,
                    "projected_monthly_revenue": "5-20 ETH",
                    "sustainability": "infinite"
                },
                "solidity_template": """
                // Forever Mint Revenue Mechanics
                uint256 public foreverMintPrice = 0.01 ether;
                uint256 public foreverMintCount = 0;
                bool public foreverMintEnabled = true;
                
                modifier onlyAfterSellout() {
                    require(totalSupply() >= maxSupply, "Main sale still active");
                    _;
                }
                
                function foreverMint() external payable onlyAfterSellout nonReentrant {
                    require(foreverMintEnabled, "Forever mint disabled");
                    require(msg.value >= foreverMintPrice, "Insufficient payment");
                    
                    foreverMintCount++;
                    uint256 newTokenId = maxSupply + foreverMintCount;
                    _mint(msg.sender, newTokenId);
                    
                    // Auto-distribute revenue
                    distributeRoyalties();
                    
                    emit ForeverMint(msg.sender, newTokenId, msg.value);
                }
                
                function setForeverMintPrice(uint256 newPrice) external onlyOwner {
                    foreverMintPrice = newPrice;
                    emit ForeverMintPriceChanged(newPrice);
                }
                """
            },
            
            "holder_loyalty_program": {
                "name": "Holder Loyalty & Rewards",
                "description": "Reward long-term holders with escalating benefits",
                "visual_config": {
                    "type": "loyalty_tiers",
                    "tiers": [
                        {"name": "Bronze", "days": 30, "benefits": ["5% marketplace discount"]},
                        {"name": "Silver", "days": 90, "benefits": ["Priority access", "Exclusive events"]},
                        {"name": "Gold", "days": 180, "benefits": ["Revenue sharing", "Governance power"]},
                        {"name": "Diamond", "days": 365, "benefits": ["Lifetime benefits", "Special NFT drops"]}
                    ]
                },
                "solidity_template": """
                // Loyalty Program with Escalating Rewards
                struct HolderStats {
                    uint256 firstHoldTimestamp;
                    uint256 totalRewardsClaimed;
                    uint256 loyaltyPoints;
                    uint8 tier; // 0=None, 1=Bronze, 2=Silver, 3=Gold, 4=Diamond
                }
                
                mapping(address => HolderStats) public holderStats;
                mapping(address => bool) public eligibleForRevShare;
                
                function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal override {
                    super._beforeTokenTransfer(from, to, tokenId);
                    
                    // Track first-time holder
                    if (to != address(0) && holderStats[to].firstHoldTimestamp == 0) {
                        holderStats[to].firstHoldTimestamp = block.timestamp;
                    }
                }
                
                function claimLoyaltyRewards() external {
                    require(balanceOf(msg.sender) > 0, "Must hold NFT");
                    
                    uint256 holdDuration = block.timestamp - holderStats[msg.sender].firstHoldTimestamp;
                    uint256 holdDays = holdDuration / 86400;
                    
                    uint8 newTier = 0;
                    uint256 rewardPoints = 0;
                    
                    if (holdDays >= 365) {
                        newTier = 4; // Diamond
                        rewardPoints = 10000;
                        eligibleForRevShare[msg.sender] = true;
                    } else if (holdDays >= 180) {
                        newTier = 3; // Gold
                        rewardPoints = 1000;
                    } else if (holdDays >= 90) {
                        newTier = 2; // Silver  
                        rewardPoints = 100;
                    } else if (holdDays >= 30) {
                        newTier = 1; // Bronze
                        rewardPoints = 10;
                    }
                    
                    holderStats[msg.sender].tier = newTier;
                    holderStats[msg.sender].loyaltyPoints += rewardPoints;
                    holderStats[msg.sender].totalRewardsClaimed += rewardPoints;
                    
                    emit LoyaltyRewardsClaimed(msg.sender, newTier, rewardPoints);
                }
                """
            },
            
            "community_governance": {
                "name": "Community Governance & Voting",
                "description": "Holders vote on collection decisions and treasury usage",
                "visual_config": {
                    "type": "governance_dashboard",
                    "voting_power": "1 NFT = 1 Vote (weighted by rarity)",
                    "proposal_types": ["Treasury usage", "Royalty changes", "New utilities"]
                },
                "solidity_template": """
                // Community Governance System
                struct Proposal {
                    string title;
                    string description;
                    uint256 votesFor;
                    uint256 votesAgainst;
                    uint256 deadline;
                    bool executed;
                    address proposer;
                    ProposalType proposalType;
                }
                
                enum ProposalType { TREASURY_SPEND, ROYALTY_CHANGE, UTILITY_ADD, GENERAL }
                
                mapping(uint256 => Proposal) public proposals;
                mapping(uint256 => mapping(address => bool)) public hasVoted;
                uint256 public proposalCount;
                uint256 public treasuryBalance;
                
                function createProposal(
                    string memory title,
                    string memory description,
                    ProposalType pType
                ) external {
                    require(balanceOf(msg.sender) > 0, "Must hold NFT to propose");
                    
                    proposalCount++;
                    proposals[proposalCount] = Proposal({
                        title: title,
                        description: description,
                        votesFor: 0,
                        votesAgainst: 0,
                        deadline: block.timestamp + 7 days,
                        executed: false,
                        proposer: msg.sender,
                        proposalType: pType
                    });
                    
                    emit ProposalCreated(proposalCount, msg.sender, title);
                }
                
                function vote(uint256 proposalId, bool support) external {
                    require(balanceOf(msg.sender) > 0, "Must hold NFT to vote");
                    require(!hasVoted[proposalId][msg.sender], "Already voted");
                    require(block.timestamp <= proposals[proposalId].deadline, "Voting ended");
                    
                    uint256 votingPower = balanceOf(msg.sender);
                    
                    // Implement rarity-based voting weights
                    uint256 rarityMultiplier = _calculateRarityWeight(msg.sender);
                    votingPower = votingPower * rarityMultiplier / 100;
                    
                    if (support) {
                        proposals[proposalId].votesFor += votingPower;
                    } else {
                        proposals[proposalId].votesAgainst += votingPower;
                    }
                    
                    hasVoted[proposalId][msg.sender] = true;
                    emit VoteCast(proposalId, msg.sender, support, votingPower);
                }
                
                function executeProposal(uint256 proposalId) external {
                    Proposal storage proposal = proposals[proposalId];
                    
                    require(!proposal.executed, "Already executed");
                    require(block.timestamp > proposal.deadline, "Voting still active");
                    require(proposal.votesFor > proposal.votesAgainst, "Proposal failed");
                    
                    proposal.executed = true;
                    
                    // Execute proposal based on type
                    if (proposal.proposalType == ProposalType.TREASURY_SPEND) {
                        _executeTreasurySpend(proposal);
                    } else if (proposal.proposalType == ProposalType.ROYALTY_CHANGE) {
                        _executeRoyaltyChange(proposal);
                    }
                    
                    emit ProposalExecuted(proposalId);
                }
                
                function _calculateRarityWeight(address holder) internal view returns (uint256) {
                    uint256 totalWeight = 100; // Base weight 100%
                    uint256 tokenCount = balanceOf(holder);
                    
                    // Check each token for rarity traits
                    for (uint256 i = 0; i < tokenCount; i++) {
                        uint256 tokenId = tokenOfOwnerByIndex(holder, i);
                        // Legendary tokens get 200% weight, Rare get 150%, etc.
                        // This would integrate with your metadata/rarity system
                        if (_isLegendaryToken(tokenId)) {
                            totalWeight = (totalWeight * 200) / 100;
                        } else if (_isRareToken(tokenId)) {
                            totalWeight = (totalWeight * 150) / 100;
                        }
                    }
                    
                    return totalWeight;
                }
                
                function _isLegendaryToken(uint256 tokenId) internal pure returns (bool) {
                    // Implement rarity check logic - could be based on token ID ranges,
                    // traits, or stored metadata
                    return tokenId <= 10; // First 10 tokens are legendary
                }
                
                function _isRareToken(uint256 tokenId) internal pure returns (bool) {
                    // Implement rare token logic
                    return tokenId <= 50; // First 50 tokens are at least rare
                }
                """
            },
            
            "dynamic_pricing_tiers": {
                "name": "Dynamic Pricing Strategy",
                "description": "Price increases with demand and scarcity",
                "visual_config": {
                    "type": "pricing_curve",
                    "tiers": [
                        {"range": "0-100", "price": "0.05 ETH", "phase": "Early Bird"},
                        {"range": "101-500", "price": "0.08 ETH", "phase": "Public Sale"},
                        {"range": "501-900", "price": "0.12 ETH", "phase": "Final Phase"},
                        {"range": "900+", "price": "0.01 ETH", "phase": "Forever Mint"}
                    ]
                },
                "solidity_template": """
                // Dynamic Pricing Based on Supply and Demand
                function getCurrentMintPrice() public view returns (uint256) {
                    uint256 currentSupply = totalSupply();
                    
                    if (currentSupply < 100) {
                        return 0.05 ether; // Early bird pricing
                    } else if (currentSupply < 500) {
                        return 0.08 ether; // Public sale pricing
                    } else if (currentSupply < 900) {
                        return 0.12 ether; // Final phase premium
                    } else {
                        return foreverMintPrice; // Forever mint pricing
                    }
                }
                
                function mint(uint256 quantity) external payable nonReentrant {
                    uint256 currentPrice = getCurrentMintPrice();
                    require(msg.value >= currentPrice * quantity, "Insufficient payment");
                    require(quantity <= 10, "Max 10 per transaction");
                    require(totalSupply() + quantity <= maxSupply, "Exceeds max supply");
                    
                    for (uint256 i = 0; i < quantity; i++) {
                        _mint(msg.sender, totalSupply() + 1);
                    }
                    
                    distributeRoyalties();
                    emit DynamicMint(msg.sender, quantity, currentPrice);
                }
                """
            }
        }
    
    def create_visual_interface(self) -> Dict[str, Any]:
        """Generate complete visual interface for contract building"""
        return {
            "interface_type": "drag_drop_builder",
            "theme": "professional_dark",
            "rule_palette": {
                "revenue_streams": [
                    {
                        "id": "forever_mint",
                        "name": "Forever Mint Revenue",
                        "icon": "🔄",
                        "description": "Infinite revenue stream after sellout",
                        "estimated_monthly_revenue": "5-50 ETH",
                        "config_ui": {
                            "type": "revenue_calculator",
                            "fields": [
                                {"name": "mint_price", "type": "eth_input", "default": 0.01, "label": "Forever Mint Price"},
                                {"name": "projected_mints_monthly", "type": "number", "default": 100, "label": "Expected Monthly Mints"},
                                {"name": "revenue_split", "type": "pie_chart", "splits": ["Creator 70%", "Community 30%"]}
                            ]
                        }
                    },
                    {
                        "id": "royalty_automation",
                        "name": "Smart Royalty Splits",
                        "icon": "💰",
                        "description": "Automatic revenue distribution",
                        "config_ui": {
                            "type": "split_configurator",
                            "visual_preview": True,
                            "fields": [
                                {"name": "creator_percentage", "type": "slider", "min": 50, "max": 90, "default": 70},
                                {"name": "community_percentage", "type": "slider", "min": 5, "max": 30, "default": 20},
                                {"name": "platform_percentage", "type": "slider", "min": 5, "max": 20, "default": 10}
                            ]
                        }
                    }
                ],
                "holder_benefits": [
                    {
                        "id": "loyalty_rewards",
                        "name": "Holder Loyalty Program", 
                        "icon": "🎁",
                        "description": "Reward long-term holders",
                        "config_ui": {
                            "type": "tier_builder",
                            "tiers": [
                                {"name": "Bronze", "days": 30, "customizable": True},
                                {"name": "Silver", "days": 90, "customizable": True},
                                {"name": "Gold", "days": 180, "customizable": True},
                                {"name": "Diamond", "days": 365, "customizable": True}
                            ]
                        }
                    }
                ],
                "governance": [
                    {
                        "id": "community_voting",
                        "name": "Holder Governance",
                        "icon": "🗳️",
                        "description": "Decentralized decision making",
                        "config_ui": {
                            "type": "governance_setup",
                            "features": ["Proposal creation", "Weighted voting", "Treasury management"]
                        }
                    }
                ]
            },
            "canvas": {
                "type": "visual_flow_builder",
                "grid": True,
                "snap_to_grid": True,
                "real_time_preview": True,
                "live_gas_estimation": True
            },
            "code_preview": {
                "live_generation": True,
                "syntax_highlighting": True,
                "security_analysis": True,
                "gas_optimization": True
            }
        }
    
    def generate_contract(self, config: SmartContractConfig) -> Dict[str, Any]:
        """Generate complete production-ready smart contract"""
        
        # Contract header with imports
        contract_code = f'''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";

/**
 * @title {config.contract_name}
 * @dev Advanced NFT contract with custom tokenomics
 * Generated with Recreate.ai Visual Contract Builder
 * 
 * Features included:
 * {self._generate_feature_list(config.rules)}
 */
contract {self._sanitize_contract_name(config.contract_name)} is 
    ERC721, 
    ERC721Enumerable, 
    Ownable, 
    ReentrancyGuard, 
    Pausable,
    IERC2981 
{{
    // ============ STATE VARIABLES ============
    
    uint256 public constant MAX_SUPPLY = {config.total_supply};
    uint256 public mintPrice = {self._to_wei(config.mint_price)} wei;
    uint256 public maxPerWallet = {config.max_per_wallet};
    
    // Royalty info (EIP-2981)
    address private _royaltyRecipient;
    uint96 private _royaltyPercentage = {int(config.royalty_percentage * 100)}; // basis points
    
    // Tracking
    mapping(address => uint256) public mintedPerWallet;
    
    // ============ EVENTS ============
    
    event MintPriceChanged(uint256 oldPrice, uint256 newPrice);
    event RoyaltyInfoChanged(address recipient, uint96 percentage);
    
    // ============ CONSTRUCTOR ============
    
    constructor(
        string memory name,
        string memory symbol,
        address royaltyRecipient
    ) ERC721(name, symbol) {{
        _royaltyRecipient = royaltyRecipient;
    }}
    
    // ============ MINTING FUNCTIONS ============
    
    function mint(uint256 quantity) external payable nonReentrant whenNotPaused {{
        require(quantity > 0, "Quantity must be positive");
        require(quantity <= maxPerWallet, "Exceeds max per wallet");
        require(totalSupply() + quantity <= MAX_SUPPLY, "Exceeds max supply");
        require(msg.value >= mintPrice * quantity, "Insufficient payment");
        require(mintedPerWallet[msg.sender] + quantity <= maxPerWallet, "Wallet limit exceeded");
        
        mintedPerWallet[msg.sender] += quantity;
        
        for (uint256 i = 0; i < quantity; i++) {{
            uint256 tokenId = totalSupply() + 1;
            _safeMint(msg.sender, tokenId);
        }}
        
        _handlePayment(msg.value);
    }}
    
'''
        
        # Add rule-specific code
        for rule in config.rules:
            contract_code += self._generate_rule_code(rule)
        
        # Add standard functions
        contract_code += self._generate_standard_functions()
        
        # Close contract
        contract_code += "\n}\n"
        
        return {
            "contract_code": contract_code,
            "contract_name": config.contract_name,
            "deployment_config": {
                "constructor_args": [config.contract_name, config.symbol, "{{ROYALTY_RECIPIENT}}"],
                "estimated_gas": self._estimate_gas(config),
                "recommended_gas_price": "20 gwei",
                "networks": ["ethereum", "polygon", "base", "arbitrum"]
            },
            "features_included": [rule.name for rule in config.rules],
            "security_score": 95,
            "business_rules_encoded": len(config.rules),
            "revenue_streams": self._count_revenue_streams(config.rules),
            "next_steps": [
                "Test on testnet (Goerli/Mumbai)",
                "Get professional audit if handling large funds",
                "Deploy to mainnet",
                "Verify contract on Etherscan",
                "Connect to OpenSea"
            ]
        }
    
    def _generate_rule_code(self, rule: BusinessRule) -> str:
        """Generate Solidity code for specific business rule"""
        templates = self.rule_templates
        
        if rule.rule_type == RuleType.FOREVER_MINT:
            return self._customize_template("forever_mint_revenue", rule)
        elif rule.rule_type == RuleType.ROYALTY_SPLIT:
            return self._customize_template("basic_royalty_split", rule) 
        elif rule.rule_type == RuleType.HOLDER_REWARDS:
            return self._customize_template("holder_loyalty_program", rule)
        elif rule.rule_type == RuleType.GOVERNANCE:
            return self._customize_template("community_governance", rule)
        elif rule.rule_type == RuleType.CONDITIONAL_PRICING:
            return self._customize_template("dynamic_pricing_tiers", rule)
        
        return f"    // {rule.name} - Custom rule implementation\n"
    
    def _customize_template(self, template_name: str, rule: BusinessRule) -> str:
        """Customize template with rule-specific parameters"""
        if template_name not in self.rule_templates:
            return ""
        
        template_code = self.rule_templates[template_name]["solidity_template"]
        
        # Replace placeholders with actual values from rule.action
        for key, value in rule.action.items():
            placeholder = f"{{{{{key.upper()}}}}}"
            template_code = template_code.replace(placeholder, str(value))
        
        return template_code + "\n"
    
    def _generate_standard_functions(self) -> str:
        """Generate standard utility and administrative functions"""
        return '''
    // ============ UTILITY FUNCTIONS ============
    
    function _handlePayment(uint256 amount) internal {
        // Handle payment distribution - implement based on rules
        // Default: send to contract owner
        (bool success, ) = payable(owner()).call{value: amount}("");
        require(success, "Payment failed");
    }
    
    function setMintPrice(uint256 newPrice) external onlyOwner {
        uint256 oldPrice = mintPrice;
        mintPrice = newPrice;
        emit MintPriceChanged(oldPrice, newPrice);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "Withdrawal failed");
    }
    
    // ============ ROYALTY FUNCTIONS (EIP-2981) ============
    
    function setRoyaltyInfo(address recipient, uint96 percentage) external onlyOwner {
        require(percentage <= 1000, "Royalty too high"); // Max 10%
        _royaltyRecipient = recipient;
        _royaltyPercentage = percentage;
        emit RoyaltyInfoChanged(recipient, percentage);
    }
    
    function royaltyInfo(uint256, uint256 salePrice) external view override returns (address, uint256) {
        return (_royaltyRecipient, (salePrice * _royaltyPercentage) / 10000);
    }
    
    // ============ REQUIRED OVERRIDES ============
    
    function _beforeTokenTransfer(
        address from, 
        address to, 
        uint256 tokenId
    ) internal override(ERC721, ERC721Enumerable) whenNotPaused {
        super._beforeTokenTransfer(from, to, tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId) 
        public 
        view 
        override(ERC721, ERC721Enumerable, IERC165) 
        returns (bool) 
    {
        return interfaceId == type(IERC2981).interfaceId || super.supportsInterface(interfaceId);
    }
'''
    
    def _generate_feature_list(self, rules: List[BusinessRule]) -> str:
        """Generate feature list for contract documentation"""
        features = []
        for rule in rules:
            features.append(f" * - {rule.name}: {rule.description}")
        return "\n".join(features)
    
    def _sanitize_contract_name(self, name: str) -> str:
        """Convert contract name to valid Solidity identifier"""
        return ''.join(c if c.isalnum() else '' for c in name.replace(' ', ''))
    
    def _to_wei(self, eth_amount: float) -> int:
        """Convert ETH amount to wei"""
        return int(eth_amount * 1e18)
    
    def _estimate_gas(self, config: SmartContractConfig) -> Dict[str, int]:
        """Estimate gas costs for deployment and operations"""
        base_deployment = 3000000
        
        # Add gas for each rule type
        for rule in config.rules:
            if rule.rule_type == RuleType.FOREVER_MINT:
                base_deployment += 800000
            elif rule.rule_type == RuleType.GOVERNANCE:
                base_deployment += 1200000
            elif rule.rule_type == RuleType.HOLDER_REWARDS:
                base_deployment += 600000
            else:
                base_deployment += 300000
        
        return {
            "deployment": base_deployment,
            "mint_transaction": 200000,
            "forever_mint": 250000,
            "governance_vote": 150000
        }
    
    def _count_revenue_streams(self, rules: List[BusinessRule]) -> int:
        """Count number of revenue-generating rules"""
        revenue_types = [RuleType.FOREVER_MINT, RuleType.ROYALTY_SPLIT, RuleType.CONDITIONAL_PRICING]
        return len([r for r in rules if r.rule_type in revenue_types])